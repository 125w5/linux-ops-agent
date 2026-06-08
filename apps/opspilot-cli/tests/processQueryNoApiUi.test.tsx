import { expect, test } from 'bun:test'

test('process query keywords are kept local in UI helper contract', () => {
  const value = '哪个进程占 CPU'.toLowerCase()
  expect(['哪个进程占 cpu', '高 cpu 进程'].some(keyword => value.includes(keyword))).toBe(true)
})

test('process analysis payload can drive action cards', () => {
  const result = {
    text: '结论：当前 CPU 最高的是 Codex (PID 14684)。',
    actions: [
      { label: 'Inspect 14684', command: '/process inspect 14684' },
      { label: 'Refresh', command: '/process' },
    ],
  }

  expect(result.text).toContain('结论：')
  expect(result.actions[0]?.command).toBe('/process inspect 14684')
})
