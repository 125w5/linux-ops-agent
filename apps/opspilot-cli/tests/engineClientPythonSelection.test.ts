import { expect, test } from 'bun:test'
import { preferredPython } from '../src/services/engineClient.js'

test('engine client prefers explicit OpsPilot python', () => {
  const old = process.env.OPSPILOT_PYTHON
  process.env.OPSPILOT_PYTHON = 'X:/conda/python.exe'
  expect(preferredPython()).toBe('X:/conda/python.exe')
  if (old === undefined) {
    delete process.env.OPSPILOT_PYTHON
  } else {
    process.env.OPSPILOT_PYTHON = old
  }
})
