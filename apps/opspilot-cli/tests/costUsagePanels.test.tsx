import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('resource events expose usage and cost counters in state', () => {
  const state = reducer(initialState, {
    type: 'engine-event',
    event: {
      event: 'ResourceUpdated',
      payload: {
        session: {
          sandbox_profile: 'safe-read',
          latency_ms: 24,
          api_calls: 2,
          estimated_tokens: 256,
          commands_executed: 3,
          output_bytes: 4096,
        },
      },
    },
  })

  expect(state.apiCalls).toBe(2)
  expect(state.estimatedTokens).toBe(256)
  expect(state.commandsExecuted).toBe(3)
  expect(state.outputBytes).toBe(4096)
})
