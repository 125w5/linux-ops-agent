import React from 'react'
import { Box, Text } from 'ink'
import type { ActionCard as ActionCardType } from '../state/events.js'
import { ActionCard } from './ActionCard.js'

export function ActionBar({ actions }: { actions: ActionCardType[] }): React.ReactElement | null {
  if (!actions.length) {
    return null
  }
  return <Box flexDirection="column" marginTop={1}>
    <Text color="gray">Actions:</Text>
    {actions.slice(0, 5).map((action, index) => <ActionCard key={`${action.command}-${index}`} action={action} index={index} />)}
  </Box>
}
