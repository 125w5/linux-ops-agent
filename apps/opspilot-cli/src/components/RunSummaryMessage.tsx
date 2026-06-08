import React from 'react'
import { Box, Text } from 'ink'
import { ActionBar } from './ActionBar.js'
import type { ActionCard } from '../state/events.js'

export function RunSummaryMessage({
  text,
  risk,
  actions,
}: {
  text: string
  risk: string
  actions: ActionCard[]
}): React.ReactElement {
  return <Box flexDirection="column">
    <Text color="cyan" bold>Run Summary</Text>
    <Text>{text}</Text>
    <Text color="gray">risk: {risk}</Text>
    <ActionBar actions={actions} />
  </Box>
}
