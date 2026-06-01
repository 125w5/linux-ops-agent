import React from 'react'
import { Text } from 'ink'
import type { Message } from '../state/events.js'
import { MessageBubble } from './MessageBubble.js'

export function MessageList({ messages }: { messages: Message[] }): React.ReactElement {
  if (!messages.length) {
    return <Text color="gray">No messages yet. Describe a fault or type /help.</Text>
  }
  return <>{messages.map((message, index) => <MessageBubble key={`${message.role}-${index}`} message={message} />)}</>
}
