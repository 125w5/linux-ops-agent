import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('run summary can appear before ReportWritten without layout state changes', () => {
  const before = { ...initialState, activePanel: 'Task' as const }
  const withSummary = reducer(before, { type: 'engine-event', event: { event: 'AssistantMessage', payload: { content: 'Diagnosis complete.\nRisk: info', actions: [{ label: 'Generate report', command: '/report' }] } } })

  expect(withSummary.messages.at(-1)?.content).toContain('Diagnosis complete')
  expect(withSummary.reportPath).toBe('')
  expect(withSummary.activePanel).toBe('Task')
})
