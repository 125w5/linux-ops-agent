import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { AppShell } from '../src/components/AppShell.js'
import { initialState } from '../src/state/appState.js'
import { makeViewport } from '../src/layout/viewport.js'

test('root workbench renders within terminal height', () => {
  const viewport = makeViewport(100, 20)
  const view = render(<AppShell state={initialState} input="" selectedActionIndex={0} searchTerm="" viewport={viewport} />)
  const frame = view.lastFrame() ?? ''

  expect(frame.split('\n').length).toBeLessThanOrEqual(20)
  view.unmount()
})

test('compact viewport avoids two page layout', () => {
  const viewport = makeViewport(70, 16)
  const view = render(<AppShell state={initialState} input="" selectedActionIndex={0} searchTerm="" viewport={viewport} />)
  const frame = view.lastFrame() ?? ''

  expect(frame.split('\n').length).toBeLessThanOrEqual(16)
  expect(frame).toContain('diag>')
  view.unmount()
})
