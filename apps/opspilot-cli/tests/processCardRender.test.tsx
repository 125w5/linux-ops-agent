import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { ProcessCard } from '../src/components/ProcessCard.js'

test('ProcessCard renders process actions without naked Ink strings', () => {
  const view = render(<ProcessCard process={{ pid: 13244, name: 'python.exe', cpu_percent: 72, memory_mb: 410 }} />)

  expect(view.lastFrame()).toContain('/process term 13244')
  view.unmount()
})
