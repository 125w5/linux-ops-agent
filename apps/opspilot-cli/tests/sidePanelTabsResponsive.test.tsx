import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { SidePanelTabs } from '../src/components/SidePanelTabs.js'

test('wide side panel shows horizontal primary tabs', () => {
  const view = render(<SidePanelTabs active="Resources" width={72} />)
  const frame = view.lastFrame() ?? ''

  expect(frame).toContain('[Task]')
  expect(frame).toContain('[Resources]')
  expect(frame.split('\n').length).toBe(1)
  view.unmount()
})

test('narrow side panel collapses tabs to one stable label', () => {
  const view = render(<SidePanelTabs active="Resources" width={42} />)
  const frame = view.lastFrame() ?? ''

  expect(frame).toContain('Panel: Resources')
  expect(frame).toContain('Tab/F2-F8')
  expect(frame).not.toContain('[Task]')
  expect(frame.split('\n').length).toBe(1)
  view.unmount()
})
