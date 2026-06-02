import { expect, test } from 'bun:test'
import { API_PROVIDER_CHOICES, API_PROVIDER_OPTIONS } from '../src/services/apiConfig.js'

test('api config wizard provider options are api only', () => {
  expect(API_PROVIDER_OPTIONS).toEqual(['deepseek', 'openai', 'anthropic', 'gemini', 'openai_compatible', 'custom'])
  expect(API_PROVIDER_OPTIONS.join(',')).not.toContain('ollama')
  expect(API_PROVIDER_OPTIONS.join(',')).not.toContain('local')
})

test('api config wizard labels expose common and gateway providers', () => {
  expect(API_PROVIDER_CHOICES.map(choice => choice.label)).toEqual(['DeepSeek V4', 'OpenAI', 'Anthropic', 'Gemini', 'OpenAI-compatible', 'Custom Remote API'])
})
