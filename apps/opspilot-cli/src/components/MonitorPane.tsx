import React from 'react'
import { Box, Text } from 'ink'
import { diskLabel, loadLabel, memoryLabel, numberValue, processRows, readObject } from '../utils/resourceFormat.js'
import { ProcessList } from './ProcessList.js'
import { Sparkline } from './Sparkline.js'
import { UsageBar } from './UsageBar.js'

export function MonitorPane({
  resources,
  history,
  compact = false,
}: {
  resources: Record<string, unknown>
  history: Record<string, unknown>[]
  compact?: boolean
}): React.ReactElement {
  const system = readObject(resources.system)
  const disk = readObject(resources.disk)
  const hasTelemetry = Object.keys(resources).length > 0
  const samplerStatus = String(resources.sampler_status ?? system.sampler_status ?? 'unknown')
  const samplerError = String(resources.sampler_error ?? system.sampler_error ?? '')
  const schemaError = readObject(resources.resource_schema).errors
  const totalMemoryGb = numberValue(system.memory_total_gb)
  const logicalCpuCount = numberValue(system.logical_cpu_count)
  const cpuRows = processRows(resources.top_cpu_processes, totalMemoryGb, logicalCpuCount)
  const memoryRows = processRows(resources.top_memory_processes, totalMemoryGb, logicalCpuCount)

  if (compact) {
    if (!hasTelemetry) {
      return <Text color="yellow">monitor waiting for first telemetry sample...</Text>
    }
    if (resources.telemetry_stalled) {
      return <Text color="red">Telemetry stalled: no ResourceUpdated received. Run /monitor doctor.</Text>
    }
    if (samplerStatus === 'error' && !cpuRows.length && !memoryRows.length) {
      return <Text color="red">monitor error: {samplerError || 'unknown sampler error'}</Text>
    }
    if (samplerStatus === 'error' || samplerStatus === 'degraded') {
      return <Text>
        <Text color="yellow">degraded </Text><Text color="gray">{samplerError || 'fallback telemetry'}</Text>
        <Text color="cyan"> CPU </Text><Text>{formatInlinePercent(system.cpu_percent)}</Text>
        <Text color="cyan"> MEM </Text><Text>{memoryLabel(system)}</Text>
        <Text color="cyan"> DISK </Text><Text>{diskLabel(disk)}</Text>
        <Text color="gray"> top {cpuRows.length}/{memoryRows.length}</Text>
      </Text>
    }
    if (samplerStatus === 'starting' || samplerStatus === 'stalled') {
      return <Text color="yellow">telemetry {samplerStatus}: waiting for ResourceUpdated...</Text>
    }
    return <Text>
      <Text color="cyan">CPU </Text><Text>{formatInlinePercent(system.cpu_percent)}</Text>
      <Text color="cyan"> MEM </Text><Text>{memoryLabel(system)}</Text>
      <Text color="cyan"> DISK </Text><Text>{diskLabel(disk)}</Text>
      <Text color="gray"> top {cpuRows.length}/{memoryRows.length}</Text>
    </Text>
  }

  return <Box flexDirection="column">
    {!hasTelemetry ? <Text color="yellow">monitor waiting for first telemetry sample...</Text> : null}
    {samplerStatus === 'warming_up' ? <Text color="yellow">sampling process CPU...</Text> : null}
    {samplerStatus === 'error' && !cpuRows.length && !memoryRows.length ? <Text color="red">monitor error: {samplerError || 'unknown sampler error'}</Text> : null}
    {samplerStatus === 'degraded' || (samplerStatus === 'error' && (cpuRows.length || memoryRows.length)) ? <Text color="yellow">degraded telemetry: {samplerError || 'fallback active'}</Text> : null}
    {Array.isArray(schemaError) && schemaError.length ? <Text color="red">schema error: {schemaError.join('; ')}</Text> : null}
    <UsageBar label="CPU" value={system.cpu_percent} detail={loadLabel(system.load_average)} />
    <UsageBar label="MEM" value={system.memory_percent} detail={memoryLabel(system)} />
    <UsageBar label="DISK" value={disk.percent ?? disk.disk_percent} detail={diskLabel(disk)} />
    {compact ? null : <Sparkline label="CPU trend" values={history.map(snapshot => readObject(snapshot.system).cpu_percent)} />}
    {compact ? null : <ProcessList title="Top CPU" rows={cpuRows} metric="cpu" />}
    {compact ? null : <ProcessList title="Top MEM" rows={memoryRows} metric="mem" />}
  </Box>
}

function formatInlinePercent(value: unknown): string {
  const number = numberValue(value)
  return number === undefined ? 'sampling' : `${Math.round(number)}%`
}
