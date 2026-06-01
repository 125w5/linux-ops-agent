import { expect, test } from 'bun:test'
import { actionByIndex, defaultActions } from '../src/actions/registry.js'

test('action cards resolve slash commands by index', () => {
  expect(actionByIndex(defaultActions, 1)?.command).toBe('/run')
  expect(actionByIndex(defaultActions, 2)?.command).toBe('/config api')
  expect(actionByIndex(defaultActions, 99)).toBeUndefined()
})
