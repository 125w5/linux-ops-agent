import React from 'react'
import { Box } from 'ink'
import { diskLabel, loadLabel, memoryLabel, numberValue, processRows, readObject } from '../utils/resourceFormat.js'
import { ProcessList } from './ProcessList.js'
import { Sparkline } from './Sparkline.js'
import { UsageBar } from './UsageBar.js'

export function MonitorPane({
  resources,
  history,
}: {
  resources: Record<string, unknown>
  history: Record<string, unknown>[]
}): React.ReactElement {
  const system = readObject(resources.system)
  const disk = readObject(resources.disk)
  const totalMemoryGb = numberValue(system.memory_total_gb)
  const cpuRows = processRows(resources.top_cpu_processes, totalMemoryGb)
  const memoryRows = processRows(resources.top_memory_processes, totalMemoryGb)

  return <Box flexDirection="column">
    <UsageBar label="CPU" value={system.cpu_percent} detail={loadLabel(system.load_average)} />
    <UsageBar label="MEM" value={system.memory_percent} detail={memoryLabel(system)} />
    <UsageBar label="DISK" value={disk.percent ?? disk.disk_percent} detail={diskLabel(disk)} />
    <Sparkline label="CPU trend" values={history.map(snapshot => readObject(snapshot.system).cpu_percent)} />
    <ProcessList title="Top CPU" rows={cpuRows} metric="cpu" />
    <ProcessList title="Top MEM" rows={memoryRows} metric="mem" />
  </Box>
}
