import React from 'react'
import type { AppState } from '../state/appState.js'
import { AppShell } from '../components/AppShell.js'

export function MainScreen({ state }: { state: AppState }): React.ReactElement {
  return <AppShell state={state} />
}
