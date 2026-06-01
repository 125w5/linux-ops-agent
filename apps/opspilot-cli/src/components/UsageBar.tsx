import React from 'react'
import { Text } from 'ink'
import { percentLabel, usageBar } from '../utils/resourceFormat.js'

export function UsageBar({
  label,
  value,
  detail,
}: {
  label: string
  value: unknown
  detail: string
}): React.ReactElement {
  return <Text>
    <Text color="cyan">{label.padEnd(5)}</Text>
    <Text color="green">{usageBar(value)}</Text>
    {'  '}
    <Text>{percentLabel(value).padEnd(6)}</Text>
    <Text color="gray">{detail}</Text>
  </Text>
}
