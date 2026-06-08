import React from 'react'
import { Text } from 'ink'
import type { AppState } from '../state/appState.js'

export function StatusLine({ state }: { state: AppState }): React.ReactElement {
  const waiting = state.responding ? ' responding' : ''
  const fallback = state.fallbackReason ? ` fallback=${state.fallbackReason}` : ''
  return <Text color="green">OpsPilot | session={state.sessionId || 'pending'} | mode={state.mode} | sandbox={state.sandboxProfile} | model={state.model} | latency={state.latencyMs}ms api={state.apiCalls}/{state.apiLatencyMs}ms{waiting}{fallback} | risk={state.risk} | status={state.status}</Text>
}
