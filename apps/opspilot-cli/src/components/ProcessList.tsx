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
      ? <Text color="gray">  n/a</Text>
      : rows.map((row, index) => (
        <Text key={`${title}-${row.name}-${index}`}>
          {'  '}
          <Text>{row.name.slice(0, 18).padEnd(18)}</Text>
          <Text color={metric === 'cpu' ? 'yellow' : 'magenta'}>
            {metric === 'cpu' ? formatProcessCpu(row).padStart(8) : formatProcessMem(row).padStart(8)}
          </Text>
        </Text>
      ))}
  </>
}
