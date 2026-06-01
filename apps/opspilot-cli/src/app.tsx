import React from 'react'
import { render } from 'ink'
import { initialState } from './state/appState.js'
import { MainScreen } from './screens/MainScreen.js'

export function startApp(): void {
  render(<MainScreen state={initialState} />)
}
