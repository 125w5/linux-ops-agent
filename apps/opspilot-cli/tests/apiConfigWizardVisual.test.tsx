import { expect, test } from 'bun:test'
import { ApiConfigWizard } from '../src/screens/ApiConfigWizard.js'

test('api config wizard shows visual provider choices without local ai', () => {
  const tree = ApiConfigWizard({ config: { provider: 'deepseek', model: 'deepseekv4', baseUrl: 'https://api.deepseek.com/v1', apiKeyEnv: 'DEEPSEEK_API_KEY' } })
  const raw = JSON.stringify(tree)

  expect(raw).toContain('API setup wizard')
  expect(raw).toContain('OpenAI')
  expect(raw).toContain('Custom Remote API')
  expect(raw.toLowerCase()).not.toContain('ollama')
  expect(raw).not.toContain('sk-')
})
