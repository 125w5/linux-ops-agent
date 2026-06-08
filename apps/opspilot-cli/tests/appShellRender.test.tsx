import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { AppShell } from '../src/components/AppShell.js'
import { initialState } from '../src/state/appState.js'

test('AppShell renders the workbench without naked Ink strings', () => {
  const view = render(<AppShell state={initialState} input="" selectedActionIndex={0} searchTerm="" />)

  expect(view.lastFrame()).toContain('session=pending')
  view.unmount()
})
