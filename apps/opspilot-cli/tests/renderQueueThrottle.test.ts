import { expect, test } from 'bun:test'
import { createRenderQueue } from '../src/state/renderQueue.js'
import type { EngineEvent } from '../src/state/events.js'

test('render queue throttles ResourceUpdated to once per second', () => {
  let now = 0
  const events: EngineEvent[] = []
  const queue = createRenderQueue(event => events.push(event), { now: () => now, resourceIntervalMs: 1000 })

  queue({ event: 'ResourceUpdated', payload: { value: 1 } })
  now = 200
  queue({ event: 'ResourceUpdated', payload: { value: 2 } })
  now = 1001
  queue({ event: 'ResourceUpdated', payload: { value: 3 } })

  expect(events.map(event => event.payload.value)).toEqual([1, 3])
})

test('render queue batches AssistantDelta but flushes tool events immediately', () => {
  let now = 0
  const events: EngineEvent[] = []
  const queue = createRenderQueue(event => events.push(event), { now: () => now, deltaIntervalMs: 80 })

  queue({ event: 'AssistantDelta', payload: { delta: 'a' } })
  now = 20
  queue({ event: 'AssistantDelta', payload: { delta: 'b' } })
  queue({ event: 'ToolStarted', payload: { step_id: 'df' } })

  expect(events[0]).toEqual({ event: 'AssistantDelta', payload: { delta: 'ab' } })
  expect(events[1].event).toBe('ToolStarted')
})
