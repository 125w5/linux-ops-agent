import React from 'react'
import { Text } from 'ink'

export function BoxLine({ label, value }: { label: string; value: string }): React.ReactElement {
  return <Text><Text color="cyan">{label}</Text> {value}</Text>
}
