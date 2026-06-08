import React from 'react'
import { Text } from 'ink'
import type { ProcessRow } from '../utils/resourceFormat.js'
import { formatProcessCpu, formatProcessMem } from '../utils/resourceFormat.js'

export function ProcessList({
  title,
  rows,
  metric,
}: {
  title: string
  rows: ProcessRow[]
  metric: 'cpu' | 'mem'
}): React.ReactElement {
  return <>
    <Text color="gray">{title}</Text>
    {rows.length === 0
      ? <Text color="gray">  No process sample yet</Text>
      : rows.map((row, index) => (
        <Text key={`${title}-${row.name}-${index}`}>
          {'  '}
          <Text>{`${row.name.slice(0, 14).padEnd(14)} ${String(row.pid ?? '').slice(0, 6).padEnd(6)}`}</Text>
          <Text color={metric === 'cpu' ? 'yellow' : 'magenta'}>
            {metric === 'cpu' ? formatProcessCpu(row).padStart(16) : formatProcessMem(row).padStart(8)}
          </Text>
        </Text>
      ))}
  </>
}
