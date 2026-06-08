import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { actionByIndex } from '../src/actions/registry.js'
import { ActionBar } from '../src/components/ActionBar.js'

const actions = [
  { label: 'Run diagnosis', command: '/run', shortcut: '1' },
  { label: 'Configure API', command: '/config api', shortcut: '2' },
]

test('number 1 maps to the first action command', () => {
  expect(actionByIndex(actions, 1)?.command).toBe('/run')
})

test('selected action can be rendered for enter execution', () => {
  const view = render(<ActionBar actions={actions} selectedIndex={1} />)
  const frame = view.lastFrame() ?? ''

  expect(frame).toContain('/config api')
  expect(frame).toContain('left/right select')
  view.unmount()
})
