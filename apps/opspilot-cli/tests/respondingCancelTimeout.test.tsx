import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('cancel clears responding via telemetry payload', () => {
  const state = reducer({ ...initialState, responding: true }, {
    type: 'engine-event',
    event: { event: 'TelemetryError', payload: { error: 'cancelled' } },
  })
  expect(state.resources.sampler_error).toBe('cancelled')
})
