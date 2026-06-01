import React from 'react'
import { Box, Text } from 'ink'
import type { PlanStep } from '../state/events.js'

export function ToolCallList({ plan }: { plan: PlanStep[] }): React.ReactElement {
  return <Box flexDirection="column"><Text color="cyan">Tool Calls</Text>{plan.map(step => <Text key={step.id}>{step.id}: {step.status ?? 'pending'}</Text>)}</Box>
}
