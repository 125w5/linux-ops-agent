import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('ResourceUpdated keeps manual scroll offset unchanged', () => {
  const state = { ...initialState, scroll: { offset: 7, viewportHeight: 5, totalLines: 30, atBottom: false } }
  const next = reducer(state, { type: 'engine-event', event: { event: 'ResourceUpdated', payload: { system: { cpu_percent: 55 } } } })

  expect(next.scroll.offset).toBe(7)
  expect(next.scroll.atBottom).toBe(false)
})
