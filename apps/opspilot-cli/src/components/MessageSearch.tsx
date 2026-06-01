import type { Message } from '../state/events.js'

export function searchMessages(messages: Message[], keyword: string): Message[] {
  const lowered = keyword.toLowerCase()
  return messages.filter(message => message.content.toLowerCase().includes(lowered))
}
