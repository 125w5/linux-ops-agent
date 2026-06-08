import { expect, test } from 'bun:test'
import { spawnSync } from 'node:child_process'

test('opspilot smoke command succeeds', () => {
  const result = spawnSync('bun', ['run', 'apps/opspilot-cli/src/main.tsx', '--smoke'], { encoding: 'utf8' })
  expect(result.status).toBe(0)
  expect(result.stdout).toContain('opspilot smoke ok')
}, 10000)
