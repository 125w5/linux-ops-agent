import React from 'react'
import { Box, Text } from 'ink'
import { RiskBadge } from './RiskBadge.js'

export function ApprovalCard({
  action,
  command,
  risk,
  sandboxProfile,
  reason,
  target,
}: {
  action: string
  command: string
  risk: string
  sandboxProfile: string
  reason: string
  target: string
}): React.ReactElement {
  const blocked = risk === 'blocked'
  return <Box flexDirection="column" borderStyle="single" borderColor={blocked ? 'red' : 'yellow'} paddingX={1}>
    <Text color={blocked ? 'red' : 'yellow'} bold>{blocked ? 'Blocked' : 'Approval'}</Text>
    <Text>action: {action}</Text>
    <Text>target: {target}</Text>
    <Text>command: {command}</Text>
    <Text>risk: <RiskBadge risk={risk} /></Text>
    <Text>sandbox: {sandboxProfile}</Text>
    <Text>{reason}</Text>
    {blocked ? <Text color="red">Approval is not available for blocked operations.</Text> : <Text color="gray">[1] Approve /approve  [2] Deny /deny</Text>}
  </Box>
}
