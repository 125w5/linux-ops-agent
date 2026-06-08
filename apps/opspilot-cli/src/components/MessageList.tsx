import React from 'react'
import { Box, Text } from 'ink'
import type { Message } from '../state/events.js'
import { MessageBubble } from './MessageBubble.js'
import { searchMessages } from './MessageSearch.js'

export function MessageList({ messages, searchTerm }: { messages: Message[]; searchTerm?: string }): React.ReactElement {
  const visibleMessages = searchTerm ? searchMessages(messages, searchTerm) : messages
  if (!visibleMessages.length) {
    return <Box flexDirection="column">
      <Text color="gray">No messages yet. Describe a fault or type /help.</Text>
      {searchTerm ? <Text color="yellow">Search: {searchTerm}</Text> : null}
    </Box>
  }
  return <Box flexDirection="column">
    {searchTerm ? <Text color="yellow">Search: {searchTerm} ({visibleMessages.length} matches)</Text> : null}
    {visibleMessages.map((message, index) => <MessageBubble key={`${message.role}-${index}`} message={message} />)}
  </Box>
}
