import React from 'react'
import { Text } from 'ink'
import type { Message } from '../state/events.js'

export function MessageBubble({ message }: { message: Message }): React.ReactElement {
  return <Text>
    <Text color={roleColor(message.role)}>{message.role.padEnd(9)}</Text>
    {'  '}
    {message.content.replace(/\n/g, '  ')}
  </Text>
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
