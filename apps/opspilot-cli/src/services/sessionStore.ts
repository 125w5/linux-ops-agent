import { writeFileSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'
import type { AppState } from '../state/appState.js'

export function saveSessionSnapshot(state: AppState, directory = 'outputs/history/opspilot-cli'): string {
  mkdirSync(directory, { recursive: true })
  const path = join(directory, `${state.sessionId || 'session'}.json`)
  writeFileSync(path, JSON.stringify(state, null, 2), 'utf8')
  return path
}
