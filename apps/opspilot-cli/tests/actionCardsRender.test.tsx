import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { ActionBar } from '../src/components/ActionBar.js'

test('ActionBar renders selectable cards without naked Ink strings', () => {
  const view = render(<ActionBar actions={[{ label: 'Run diagnosis', command: '/run' }, { label: 'Configure API', command: '/config api' }]} selectedIndex={0} />)

  expect(view.lastFrame()).toContain('/run')
  view.unmount()
})
