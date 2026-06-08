import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { ApiConfigWizard } from '../src/screens/ApiConfigWizard.js'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('api wizard provider selection moves through list', () => {
  const state = reducer(initialState, { type: 'api-wizard-provider', delta: 1 })

  expect(state.apiWizard.selectedProviderIndex).toBe(1)
})

test('api wizard renders provider selection list without local ai options', () => {
  const view = render(<ApiConfigWizard config={{ provider: 'deepseek', model: 'deepseekv4', baseUrl: 'https://api.deepseek.com/v1', apiKeyEnv: 'DEEPSEEK_API_KEY' }} wizard={{ step: 'provider', selectedProviderIndex: 1 }} />)
  const frame = view.lastFrame() ?? ''

  expect(frame).toContain('OpenAI')
  expect(frame.toLowerCase()).not.toContain('ollama')
  expect(frame.toLowerCase()).not.toContain('local')
  view.unmount()
})
