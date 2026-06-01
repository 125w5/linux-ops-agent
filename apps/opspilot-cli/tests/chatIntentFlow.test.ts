import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('assistant events can expose action cards', () => {
  const state = reducer(initialState, {
    type: 'engine-event',
    event: { event: 'AssistantMessage', payload: { content: 'plan ready', actions: [{ label: 'Run diagnosis', command: '/run' }] } },
  })

  expect(state.actions[0].command).toBe('/run')
  expect(state.messages.at(-1)?.actions?.[0].label).toBe('Run diagnosis')
})
