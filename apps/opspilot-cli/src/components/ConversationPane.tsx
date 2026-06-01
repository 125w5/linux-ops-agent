import React from 'react'
import { Box, Text } from 'ink'
import type { Message } from '../state/events.js'

export function ConversationPane({ messages }: { messages: Message[] }): React.ReactElement {
  return <Box flexDirection="column"><Text color="cyan">Conversation</Text>{messages.slice(-8).map((message, index) => <Text key={index}>{message.role}: {message.content}</Text>)}</Box>
}
