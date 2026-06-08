import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('assistant streaming events update one visible message', () => {
  const started = reducer(initialState, {
    type: 'engine-event',
    event: { event: 'AssistantMessageStarted', payload: { session_id: 's1' } },
  })
  const delta = reducer(started, {
    type: 'engine-event',
    event: { event: 'AssistantDelta', payload: { session_id: 's1', delta: 'hello' } },
  })
  const done = reducer(delta, {
    type: 'engine-event',
    event: { event: 'AssistantMessage', payload: { session_id: 's1', content: 'hello', actions: [{ label: 'Tools', command: '/tools' }] } },
  })

  expect(done.messages.at(-1)?.content).toBe('hello')
  expect(done.messages.filter(message => message.role === 'assistant').at(-1)?.actions?.[0].command).toBe('/tools')
})
