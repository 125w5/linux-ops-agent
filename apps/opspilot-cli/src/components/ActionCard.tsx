import React from 'react'
import { Box, Text } from 'ink'
import type { ActionCard as ActionCardType } from '../state/events.js'

export function ActionCard({ action, index, selected = false }: { action: ActionCardType; index: number; selected?: boolean }): React.ReactElement {
  return <Box marginRight={1}>
    <Box marginRight={1}>
      <Text backgroundColor={selected ? 'cyan' : undefined} color={selected ? 'black' : 'gray'}>{action.shortcut ?? String(index + 1)}</Text>
    </Box>
    <Box marginRight={1}>
      <Text bold={selected}>{action.label}</Text>
    </Box>
    <Text color="gray">{action.command}</Text>
    {action.risk ? <Text color="yellow"> {action.risk}</Text> : null}
  </Box>
}
