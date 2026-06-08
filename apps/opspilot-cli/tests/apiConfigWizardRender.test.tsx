import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { ApiConfigWizard } from '../src/screens/ApiConfigWizard.js'

test('ApiConfigWizard renders provider choices without naked Ink strings', () => {
  const view = render(<ApiConfigWizard config={{ provider: 'deepseek', model: 'deepseekv4', baseUrl: 'https://api.deepseek.com/v1', apiKeyEnv: 'DEEPSEEK_API_KEY' }} />)

  expect(view.lastFrame()).toContain('API setup wizard')
  view.unmount()
})
