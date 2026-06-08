import { expect, test } from 'bun:test'
import { formatProcessCpu, percentLabel, processRows, usageBar } from '../src/utils/resourceFormat.js'

test('raw process CPU 655 percent is normalized for display', () => {
  const rows = processRows([{ name: 'hot-process-name-that-is-too-long', raw_cpu_percent: 655, logical_cpu_count: 10 }])

  expect(formatProcessCpu(rows[0])).toBe('65.5%/655% raw')
  expect(rows[0].name.length).toBeLessThanOrEqual(18)
})

test('system CPU display clamps to 100 percent', () => {
  expect(percentLabel(655)).toBe('100%')
  expect(usageBar(655)).not.toContain('655')
})
