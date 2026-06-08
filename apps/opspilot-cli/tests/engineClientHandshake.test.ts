import { expect, test } from 'bun:test'
import { EngineClient } from '../src/services/engineClient.js'

test('engine client session.start returns session id and cwd', async () => {
  const client = new EngineClient()
  try {
    const response = await client.request('session.start', { target: 'localhost', mode: 'readonly', task: 'disk' }, 2000)
    expect(response.error).toBeUndefined()
    expect((response.result as Record<string, unknown>).session_id).toBeTruthy()
    expect((response.result as Record<string, unknown>).cwd).toContain('linux-ops-agent')
  } finally {
    client.close()
  }
}, 5000)
