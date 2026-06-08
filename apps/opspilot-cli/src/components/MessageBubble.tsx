import React from 'react'
import { Box, Text } from 'ink'
import type { Message } from '../state/events.js'
import { ActionBar } from './ActionBar.js'
import { ToolSummaryMessage } from './ToolSummaryMessage.js'

export function MessageBubble({ message }: { message: Message }): React.ReactElement {
  const isTool = message.role === 'tool'
  return <Box flexDirection="column" marginBottom={1}>
    <Box>
      <Box marginRight={1}>
        <Text color={roleColor(message.role)} bold>{roleLabel(message.role)}</Text>
      </Box>
      {isTool ? <ToolSummaryMessage name={message.content.slice(0, 24)} status="folded" /> : <Text>{message.content}</Text>}
    </Box>
    {message.actions?.length ? <ActionBar actions={message.actions} /> : null}
  </Box>
}

function roleColor(role: Message['role']): string {
  if (role === 'assistant') {
    return 'cyan'
  }
  if (role === 'user') {
    return 'green'
  }
  if (role === 'tool') {
    return 'yellow'
  }
  return 'gray'
}

function roleLabel(role: Message['role']): string {
  if (role === 'assistant') return 'assistant'
  if (role === 'user') return 'you'
  if (role === 'tool') return 'tool'
  return 'system'
}
