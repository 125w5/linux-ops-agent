import { useCallback, useMemo } from 'react'
import type { EngineEvent } from '../state/events.js'
import { createRenderQueue } from '../state/renderQueue.js'

export function useThrottledEvents(dispatch: (event: EngineEvent) => void): (event: string, payload: Record<string, unknown>) => void {
  const queue = useMemo(() => createRenderQueue(dispatch), [dispatch])
  return useCallback((event, payload) => queue({ event, payload }), [queue])
}
