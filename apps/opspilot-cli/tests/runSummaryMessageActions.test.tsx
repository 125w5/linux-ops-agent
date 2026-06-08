import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { RunSummaryMessage } from '../src/components/RunSummaryMessage.js'

test('run summary message includes next actions', () => {
  const view = render(<RunSummaryMessage text="Diagnosis complete.\nKey evidence: df -h" risk="warning" actions={[{ label: 'Show raw', command: '/raw' }, { label: 'Generate report', command: '/report' }]} />)
  const frame = view.lastFrame() ?? ''

  expect(frame).toContain('Diagnosis complete')
  expect(frame).toContain('/raw')
  expect(frame).toContain('/report')
  view.unmount()
})
