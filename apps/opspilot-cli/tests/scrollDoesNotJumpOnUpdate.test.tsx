import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('resource updates do not reset conversation scroll', () => {
  const state = { ...initialState, scroll: { offset: 3, viewportHeight: 5, totalLines: 20, atBottom: false } }
  const next = reducer(state, { type: 'engine-event', event: { event: 'ResourceUpdated', payload: { system: { cpu_percent: 1 } } } })

  expect(next.scroll.offset).toBe(3)
  expect(next.scroll.atBottom).toBe(false)
})

test('new message preserves manual scroll position when not at bottom', () => {
  const messages = Array.from({ length: 20 }, (_, index) => ({ role: 'assistant' as const, content: `message ${index}` }))
  const state = { ...initialState, messages, scroll: { offset: 2, viewportHeight: 5, totalLines: 20, atBottom: false } }
  const next = reducer(state, { type: 'message', message: { role: 'assistant', content: 'new evidence' } })

  expect(next.scroll.offset).toBe(2)
})
