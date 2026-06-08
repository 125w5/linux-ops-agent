import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { ConversationViewport } from '../src/components/ConversationViewport.js'
import type { Message } from '../src/state/events.js'

test('conversation viewport renders only visible virtual lines', () => {
  const messages: Message[] = Array.from({ length: 20 }, (_, index) => ({ role: 'assistant', content: `message-${index}` }))
  const view = render(<ConversationViewport messages={messages} scroll={{ offset: 10, viewportHeight: 4, totalLines: 20, atBottom: false }} height={4} width={60} />)
  const frame = view.lastFrame() ?? ''

  expect(frame).toContain('message-10')
  expect(frame).not.toContain('message-0')
  expect(frame.split('\n').length).toBeLessThanOrEqual(4)
  view.unmount()
})
