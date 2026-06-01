import React from 'react'
import { Text } from 'ink'

export function ToolSummaryMessage({ name, status }: { name: string; status: string }): React.ReactElement {
  return <Text><Text color="yellow">tool</Text>  {name} {'->'} {status}</Text>
}
