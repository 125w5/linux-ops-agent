import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('applies session, plan, evidence, resource and report events', () => {
  const session = reducer(initialState, {
    type: 'engine-event',
    event: { event: 'SessionStarted', payload: { session_id: 's1', target: 'localhost', mode: 'demo' } },
  })
  const planned = reducer(session, {
    type: 'engine-event',
    event: { event: 'PlanCreated', payload: { steps: [{ id: 'disk.df', name: 'df', command: 'df -h', risk: 'low' }] } },
  })
  const evidence = reducer(planned, {
    type: 'engine-event',
    event: { event: 'EvidenceAdded', payload: { items: [{ content: '根目录使用率正常' }] } },
  })
  const resources = reducer(evidence, {
    type: 'engine-event',
    event: { event: 'ResourceUpdated', payload: { system: { cpu_percent: 12 } } },
  })
  const report = reducer(resources, {
    type: 'engine-event',
    event: { event: 'ReportWritten', payload: { markdown_path: 'reports/demo.md' } },
  })

  expect(report.sessionId).toBe('s1')
  expect(report.plan[0].status).toBe('pending')
  expect(report.evidence[0]).toContain('根目录')
  expect(report.resources.system).toEqual({ cpu_percent: 12 })
  expect(report.reportPath).toBe('reports/demo.md')
})
