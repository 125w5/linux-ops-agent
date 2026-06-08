import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('tool started and finished events become conversation progress messages', () => {
  const running = reducer(initialState, { type: 'engine-event', event: { event: 'ToolStarted', payload: { step_id: 'df', command: 'df -h' } } })
  const done = reducer(running, { type: 'engine-event', event: { event: 'ToolFinished', payload: { step_id: 'df', command: 'df -h', status: 0 } } })

  expect(running.messages.some(message => message.role === 'tool' && message.content.includes('[running]'))).toBe(true)
  expect(done.messages.some(message => message.role === 'tool' && message.content.includes('[done]'))).toBe(true)
})
