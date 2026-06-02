import { expect, test } from 'bun:test'
import { envCommand, providerPatch } from '../src/services/apiConfig.js'

test('api config wizard data stores env var name only', () => {
  const patch = providerPatch({
    provider: 'openai_compatible',
    type: 'openai-compatible',
    model: 'deepseek-chat',
    baseUrl: 'https://api.deepseek.com/v1',
    apiKeyEnv: 'DEEPSEEK_API_KEY',
  })

  expect(JSON.stringify(patch)).toContain('DEEPSEEK_API_KEY')
  expect(JSON.stringify(patch)).not.toContain('sk-')
  expect(envCommand('DEEPSEEK_API_KEY')).toContain('DEEPSEEK_API_KEY')
})
