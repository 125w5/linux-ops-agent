import { expect, test } from 'bun:test'
import { assertApiOnlyProvider, providerPatch, validateRemoteBaseUrl } from '../src/services/apiConfig.js'

test('provider options reject ollama and local names', () => {
  expect(() => assertApiOnlyProvider('ollama')).toThrow('OpsPilot 已禁用本地 AI')
  expect(() => assertApiOnlyProvider('local')).toThrow('OpsPilot 已禁用本地 AI')
})

test('api config rejects localhost base url', () => {
  expect(() => validateRemoteBaseUrl('http://localhost:11434')).toThrow('OpsPilot 已禁用本地 AI')
  expect(() => validateRemoteBaseUrl('http://127.0.0.1:11434')).toThrow('OpsPilot 已禁用本地 AI')
  expect(() => validateRemoteBaseUrl('http://192.168.1.20/v1')).toThrow('OpsPilot 已禁用本地 AI')
})

test('provider patch remains remote api only', () => {
  expect(() => providerPatch({ provider: 'custom', model: 'x', baseUrl: 'https://relay.example.com/v1', apiKeyEnv: 'CUSTOM_API_KEY' })).not.toThrow()
})
