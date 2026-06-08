import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { SidePanel } from '../src/components/SidePanel.js'
import { reducer } from '../src/state/reducer.js'
import { initialState } from '../src/state/appState.js'

test('side panel tabs show only the active panel body', () => {
  const state = reducer(initialState, { type: 'side-panel', panel: 'Resources' })
  const view = render(<SidePanel state={state} height={12} />)
  const frame = view.lastFrame() ?? ''

  expect(frame).toContain('Resources')
  expect(frame).toContain('CPU')
  expect(frame).not.toContain('Current Task')
  view.unmount()
})

test('tab action advances side panel', () => {
  const state = reducer(initialState, { type: 'side-panel-next' })

  expect(state.activePanel).toBe('Evidence')
})
