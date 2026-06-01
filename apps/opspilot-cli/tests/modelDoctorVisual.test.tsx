import { expect, test } from 'bun:test'
import type { ModelDoctorRow } from '../src/screens/ModelScreen.js'

test('model doctor rows carry provider status model and note', () => {
  const row: ModelDoctorRow = { provider: 'openai', status: 'missing env', model: 'gpt-4o-mini', note: 'OPENAI_API_KEY' }

  expect(row.provider).toBe('openai')
  expect(row.status).toContain('missing')
  expect(row.note).toContain('OPENAI_API_KEY')
})
