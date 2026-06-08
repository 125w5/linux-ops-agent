import React from 'react'
import { Box, Text } from 'ink'

export type ProcessRow = {
  pid: string | number
  name: string
  cpu_percent?: number
  raw_cpu_percent?: number
  memory_percent?: number
  memory_mb?: number
}

export function ProcessCard({ process }: { process: ProcessRow }): React.ReactElement {
  return <Box flexDirection="column" borderStyle="single" borderColor="gray" paddingX={1} marginBottom={1}>
    <Text bold>{process.name} <Text color="gray">PID {process.pid}</Text></Text>
    <Text>CPU {formatCpu(process)} MEM {formatMemory(process.memory_mb, process.memory_percent)}</Text>
    <Text color="gray">Actions</Text>
    <Text>[1] Inspect  /process inspect {process.pid}</Text>
    <Text>[2] Show tree  /process tree {process.pid}</Text>
    <Text>[3] SIGTERM  /process term {process.pid}</Text>
    <Text>[4] SIGKILL  /process kill {process.pid}</Text>
  </Box>
}

function formatPercent(value: number | undefined): string {
  return value === undefined ? 'n/a' : `${value.toFixed(1)}%`
}

function formatCpu(process: ProcessRow): string {
  const normalized = formatPercent(process.cpu_percent)
  if (process.raw_cpu_percent !== undefined && process.cpu_percent !== undefined && Math.abs(process.raw_cpu_percent - process.cpu_percent) > 0.1) {
    return `${normalized} system / ${process.raw_cpu_percent.toFixed(0)}% raw`
  }
  return normalized
}

function formatMemory(memoryMb: number | undefined, memoryPercent: number | undefined): string {
  if (memoryMb !== undefined) {
    return `${Math.round(memoryMb)}MB`
  }
  return formatPercent(memoryPercent)
}
