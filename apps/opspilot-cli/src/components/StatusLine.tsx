import React from 'react'
import { Text } from 'ink'
import type { AppState } from '../state/appState.js'

export function StatusLine({ state }: { state: AppState }): React.ReactElement {
  return <Text color="green">OpsPilot | session={state.sessionId || 'pending'} | mode={state.mode} | model={state.model} | risk={state.risk} | status={state.status}</Text>
}
