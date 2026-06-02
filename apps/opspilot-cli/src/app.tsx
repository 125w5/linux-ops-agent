import React from 'react'
import { render } from 'ink'
import { initialState } from './state/appState.js'
import { MainScreen } from './screens/MainScreen.js'

export type StartAppOptions = {
  target?: string
  mode?: string
}

export function startApp(options: StartAppOptions = {}): void {
  render(<MainScreen initialState={initialState} target={options.target ?? 'localhost'} mode={options.mode ?? 'readonly'} />)
}
