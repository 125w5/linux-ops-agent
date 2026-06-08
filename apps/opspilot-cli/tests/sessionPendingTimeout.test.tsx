import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('engine failed event replaces endless pending', () => {
  const state = reducer(initialState, { type: 'engine-failed', payload: { message: 'session.start timed out', cwd: 'x', stderr: ['bad'] } })
  expect(state.engine.status).toBe('failed')
  expect(state.status).toBe('EngineFailed')
  expect(state.engine.stderr[0]).toBe('bad')
})
