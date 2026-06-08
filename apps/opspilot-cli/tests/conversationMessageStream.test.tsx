import { expect, test } from 'bun:test'
import { MessageList } from '../src/components/MessageList.js'
import type { Message } from '../src/state/events.js'

test('conversation message stream keeps role blocks and filters search', () => {
  const messages: Message[] = [
    { role: 'user', content: '磁盘满了' },
    { role: 'assistant', content: 'I will inspect evidence.' },
    { role: 'tool', content: 'df -h output' },
  ]
  const tree = MessageList({ messages, searchTerm: 'df' })

  expect(textOf(tree)).toContain('1  matches')
  expect(JSON.stringify(tree)).not.toContain('Conversation history')
})

function textOf(value: unknown): string {
  if (typeof value === 'string' || typeof value === 'number') return String(value)
  if (Array.isArray(value)) return value.map(textOf).join(' ')
  if (value && typeof value === 'object') return textOf((value as { props?: { children?: unknown } }).props?.children)
  return ''
}
