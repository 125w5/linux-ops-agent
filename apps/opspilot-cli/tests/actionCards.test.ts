import { expect, test } from 'bun:test'
import { actionByIndex, apiConfigActions, defaultActions, modelActions } from '../src/actions/registry.js'

test('action cards resolve slash commands by index', () => {
  expect(actionByIndex(defaultActions, 1)?.command).toBe('/run')
  expect(actionByIndex(defaultActions, 2)?.command).toBe('/config api')
  expect(actionByIndex(defaultActions, 99)).toBeUndefined()
})

test('api config actions expose provider menu', () => {
  expect(apiConfigActions().map(action => action.label)).toEqual(['DeepSeek V4', 'OpenAI', 'Anthropic', 'Gemini', 'OpenAI-compatible', 'Custom Remote API'])
  expect(apiConfigActions().map(action => action.command)).toContain('/config api deepseek')
  expect(apiConfigActions().map(action => action.command)).toContain('/config api openai_compatible')
})

test('model actions expose visual choices', () => {
  expect(modelActions().map(action => action.command)).toEqual(['/model list', '/model doctor', '/config api'])
})
