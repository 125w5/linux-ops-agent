import { expect, test } from 'bun:test'
import { providerPatch } from '../src/services/apiConfig.js'

test('builds provider patch using env var name instead of api key', () => {
  const patch = providerPatch({
    provider: 'openai',
    model: 'gpt-4.1-mini',
    baseUrl: 'https://api.openai.com/v1',
    apiKeyEnv: 'OPENAI_API_KEY',
  })

  expect(patch).toEqual({
    providers: {
      default: 'openai',
      openai: {
        type: 'openai-compatible',
        model: 'gpt-4.1-mini',
        base_url: 'https://api.openai.com/v1',
        api_key_env: 'OPENAI_API_KEY',
      },
    },
    profiles: {
      default: {
        provider: 'openai',
        model: 'gpt-4.1-mini',
      },
    },
  })
  expect(JSON.stringify(patch)).not.toContain('sk-')
})
