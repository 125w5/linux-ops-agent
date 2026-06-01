import React from 'react'
import { Text } from 'ink'

export function ApprovalDialog({ pending }: { pending: boolean }): React.ReactElement | null {
  return pending ? <Text color="yellow">Approval required: /approve or /deny</Text> : null
}
