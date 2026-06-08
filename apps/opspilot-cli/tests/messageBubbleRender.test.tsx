import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { MessageBubble } from '../src/components/MessageBubble.js'

test('MessageBubble renders without naked Ink strings', () => {
  const view = render(<MessageBubble message={{ role: 'assistant', content: '诊断完成', actions: [{ label: 'Show raw', command: '/raw' }] }} />)

  expect(view.lastFrame()).toContain('assistant')
  view.unmount()
})
