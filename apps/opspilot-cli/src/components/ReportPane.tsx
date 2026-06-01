import React from 'react'
import { Text } from 'ink'

export function ReportPane({ path }: { path: string }): React.ReactElement {
  return <Text color="cyan">Report {path || 'pending'}</Text>
}
