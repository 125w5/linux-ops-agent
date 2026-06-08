import { expect, test } from 'bun:test'
import { RunSummaryMessage } from '../src/components/RunSummaryMessage.js'

test('run summary message renders conclusion and actions', () => {
  const raw = JSON.stringify(RunSummaryMessage({ text: 'Diagnosis complete.\nRisk: warning', risk: 'warning', actions: [{ label: 'Show raw', command: '/raw' }] }))

  expect(raw).toContain('Diagnosis complete')
  expect(raw).toContain('/raw')
  expect(raw).toContain('warning')
})
