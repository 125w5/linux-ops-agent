import type { EngineEvent } from './events.js'

export type RenderQueueOptions = {
  resourceIntervalMs?: number
  deltaIntervalMs?: number
  now?: () => number
}

export function createRenderQueue(
  dispatch: (event: EngineEvent) => void,
  options: RenderQueueOptions = {},
): (event: EngineEvent) => void {
  const resourceIntervalMs = options.resourceIntervalMs ?? 1000
  const deltaIntervalMs = options.deltaIntervalMs ?? 80
  const now = options.now ?? (() => Date.now())
  let lastResourceAt = -Infinity
  let lastDeltaAt = 0
  let pendingDelta = ''

  return event => {
    if (event.event === 'ResourceUpdated') {
      const current = now()
      if (current - lastResourceAt < resourceIntervalMs) {
        return
      }
      lastResourceAt = current
      dispatch(event)
      return
    }

    if (event.event === 'AssistantDelta') {
      pendingDelta += String(event.payload.delta ?? '')
      const current = now()
      if (current - lastDeltaAt < deltaIntervalMs) {
        return
      }
      lastDeltaAt = current
      dispatch({ event: 'AssistantDelta', payload: { ...event.payload, delta: pendingDelta } })
      pendingDelta = ''
      return
    }

    if (pendingDelta) {
      dispatch({ event: 'AssistantDelta', payload: { delta: pendingDelta } })
      pendingDelta = ''
    }
    dispatch(event)
  }
}
