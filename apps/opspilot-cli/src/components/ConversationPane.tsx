import React from 'react'
import { Box } from 'ink'
import type { Message } from '../state/events.js'
import { MessageList } from './MessageList.js'

export function ConversationPane({ messages }: { messages: Message[] }): React.ReactElement {
  return <Box flexDirection="column">
    <MessageList messages={messages.slice(-8)} />
  </Box>
}
