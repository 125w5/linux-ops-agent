import React from 'react'
import { Text } from 'ink'
import { sparkline } from '../utils/resourceFormat.js'

export function Sparkline({ label, values }: { label: string; values: unknown[] }): React.ReactElement {
  return <Text color="gray">{label} {sparkline(values)}</Text>
}
