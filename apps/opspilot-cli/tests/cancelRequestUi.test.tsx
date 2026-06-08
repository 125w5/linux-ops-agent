import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('cancel event clears responding status through resources session payload', () => {
  const next = reducer(initialState, {
    type: 'engine-event',
    event: {
      event: 'ResourceUpdated',
      payload: {
        event: 'ResourceUpdated',
        timestamp: 1,
        sampler_status: 'ready',
        platform: 'win',
        logical_cpu_count: 8,
        system_cpu_percent: 1,
        memory: { total_bytes: 1, used_bytes: 1, percent: 1 },
        disk: { mount: 'D:', total_bytes: 1, used_bytes: 1, percent: 1 },
        top_cpu: [],
        top_memory: [],
        session: { responding: false, fallback_reason: 'cancelled', latency_trace: { total_turn_ms: 3 } },
      },
    },
  })
  expect(next.responding).toBe(false)
  expect(next.fallbackReason).toBe('cancelled')
  expect(next.latencyTrace.total_turn_ms).toBe(3)
})
