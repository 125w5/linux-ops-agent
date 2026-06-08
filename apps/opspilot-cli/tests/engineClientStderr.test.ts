import { expect, test } from 'bun:test'
import { EngineClient } from '../src/services/engineClient.js'

test('engine client exposes stderr on failed spawn', async () => {
  const client = new EngineClient('python', ['-c', 'import sys; print("boom", file=sys.stderr); sys.exit(7)'])
  const response = await client.request('session.start', {}, 500)
  expect(response.error).toBeTruthy()
  expect(JSON.stringify(response.error)).toContain('engine closed')
  client.close()
})
