import { expect, test } from 'bun:test'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('assistant placeholder is replaced when streaming starts', () => {
  const withPlaceholder = reducer(initialState, { type: 'message', message: { role: 'assistant', content: '收到，正在判断任务类型...' } })
  const started = reducer(withPlaceholder, { type: 'engine-event', event: { event: 'AssistantMessageStarted', payload: {} } })
  const delta = reducer(started, { type: 'engine-event', event: { event: 'AssistantDelta', payload: { delta: 'hello' } } })

  expect(delta.messages.filter(message => message.role === 'assistant').at(-1)?.content).toBe('hello')
  expect(delta.messages.some(message => message.content === '收到，正在判断任务类型...')).toBe(false)
})
