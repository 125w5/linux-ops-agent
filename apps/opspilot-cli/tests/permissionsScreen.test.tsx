import { expect, test } from 'bun:test'
import { slashCommands } from '../src/commands/slashCommands.js'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('permissions command is registered and session stores sandbox profile', () => {
  expect(slashCommands.map(command => command.name)).toContain('/permissions')

  const state = reducer(initialState, {
    type: 'engine-event',
    event: { event: 'SessionStarted', payload: { session_id: 's1', sandbox_profile: 'ops-read', latency_ms: 12 } },
  })

  expect(state.sandboxProfile).toBe('ops-read')
  expect(state.latencyMs).toBe(12)
})
