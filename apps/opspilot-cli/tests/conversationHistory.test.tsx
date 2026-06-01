import { expect, test } from 'bun:test'
import { searchMessages } from '../src/components/MessageSearch.js'
import type { Message } from '../src/state/events.js'

test('conversation history distinguishes roles and supports search', () => {
  const messages: Message[] = [
    { role: 'user', content: 'disk is full' },
    { role: 'assistant', content: 'I will create a plan.' },
    { role: 'tool', content: 'df -h -> done' },
  ]

  expect(searchMessages(messages, 'disk')[0].role).toBe('user')
  expect(searchMessages(messages, 'done')[0].role).toBe('tool')
})
