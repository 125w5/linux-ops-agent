import { expect, test } from 'bun:test'
import { ProcessCard } from '../src/components/ProcessCard.js'

test('process card exposes inspect tree and kill actions', () => {
  const tree = ProcessCard({ process: { pid: 13244, name: 'python.exe', cpu_percent: 72, memory_mb: 410 } })
  const raw = textOf(tree)

  expect(raw).toContain('/process inspect 13244')
  expect(raw).toContain('/process term 13244')
  expect(raw).toContain('/process kill 13244')
})

function textOf(value: unknown): string {
  if (typeof value === 'string' || typeof value === 'number') return String(value)
  if (Array.isArray(value)) return value.map(textOf).join('')
  if (value && typeof value === 'object') return textOf((value as { props?: { children?: unknown } }).props?.children)
  return ''
}
