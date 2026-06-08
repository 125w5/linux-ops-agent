import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { ConversationPane } from '../src/components/ConversationPane.js'

test('ConversationPane renders message stream without naked Ink strings', () => {
  const view = render(<ConversationPane messages={[{ role: 'user', content: '磁盘满了' }, { role: 'tool', content: 'df -h output' }]} searchTerm="" />)

  expect(view.lastFrame()).toContain('you')
  view.unmount()
})
