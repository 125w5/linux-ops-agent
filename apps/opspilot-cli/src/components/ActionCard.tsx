import React from 'react'
import { Text } from 'ink'
import type { ActionCard as ActionCardType } from '../state/events.js'

export function ActionCard({ action, index }: { action: ActionCardType; index: number }): React.ReactElement {
  return <Text>
    <Text color="cyan">[{index + 1}]</Text>
    {' '}
    <Text>{action.label.padEnd(16)}</Text>
    <Text color="gray">{action.command}</Text>
  </Text>
}
