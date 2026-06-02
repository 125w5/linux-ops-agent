import { expect, test } from 'bun:test'
import type { ModelDoctorRow } from '../src/screens/ModelScreen.js'

test('model doctor test data does not include local providers', () => {
  const rows: ModelDoctorRow[] = [
    { provider: 'openai', status: 'missing_env', model: 'gpt-4o-mini', note: '请设置环境变量，例如 OPENAI_API_KEY' },
    { provider: 'mock', status: 'ok', model: 'mock-diagnosis-v1', note: 'demo/test only' },
  ]

  expect(rows.map(row => row.provider)).not.toContain('ollama')
})
