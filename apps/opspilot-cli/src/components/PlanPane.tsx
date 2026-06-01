import React from 'react'
import { Box, Text } from 'ink'
import type { PlanStep } from '../state/events.js'

export function PlanPane({ plan }: { plan: PlanStep[] }): React.ReactElement {
  return <Box flexDirection="column"><Text color="cyan">Plan</Text>{plan.length === 0 ? <Text>no plan yet</Text> : plan.map(step => <Text key={step.id}>[{step.status ?? 'pending'}] {step.name}</Text>)}</Box>
}
