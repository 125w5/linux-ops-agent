import { expect, test } from 'bun:test'
import { normalizeResourceEvent, validateResourceEvent } from '../src/services/resourceEventValidator.js'

test('ResourceUpdated missing fields reports schema error', () => {
  const validation = validateResourceEvent({ event: 'ResourceUpdated' })
  expect(validation.ok).toBe(false)
  expect(validation.errors.join(';')).toContain('missing memory')
})

test('ResourceUpdated normalizes new schema to monitor view model', () => {
  const value = normalizeResourceEvent({
    event: 'ResourceUpdated',
    timestamp: 1,
    sampler_status: 'ready',
    platform: 'win',
    logical_cpu_count: 10,
    system_cpu_percent: 12,
    memory: { total_bytes: 1024 ** 3, used_bytes: 512 ** 3, percent: 50 },
    disk: { mount: 'D:', total_bytes: 1024 ** 3, used_bytes: 256 ** 3, percent: 25 },
    top_cpu: [{ pid: 1, name: 'edge', raw_cpu_percent: 655, normalized_cpu_percent: 65.5, memory_bytes: 1024 }],
    top_memory: [],
  })
  expect((value.system as Record<string, unknown>).cpu_percent).toBe(12)
  expect(Array.isArray(value.top_cpu_processes)).toBe(true)
})
