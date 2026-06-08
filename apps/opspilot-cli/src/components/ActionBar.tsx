import React from 'react'
import { Box, Text } from 'ink'
import type { ActionCard as ActionCardType } from '../state/events.js'
import { ActionCard } from './ActionCard.js'

export function ActionBar({ actions, selectedIndex = 0 }: { actions: ActionCardType[]; selectedIndex?: number }): React.ReactElement | null {
  if (!actions.length) {
    return null
  }
  return <Box flexDirection="column" height={3} overflow="hidden">
    <Text color="gray">Actions: 1-9 run | left/right select | Enter run</Text>
    <Box>
      {actions.slice(0, 9).map((action, index) => <ActionCard key={`${action.command}-${index}`} action={action} index={index} selected={index === selectedIndex} />)}
    </Box>
  </Box>
}
