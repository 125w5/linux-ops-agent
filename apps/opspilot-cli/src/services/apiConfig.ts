export type ApiProviderConfig = {
  provider: string
  type?: string
  model: string
  baseUrl?: string
  apiKeyEnv?: string
}

export const API_PROVIDER_OPTIONS = ['deepseek', 'openai', 'anthropic', 'gemini', 'openai_compatible', 'custom'] as const
export const API_PROVIDER_CHOICES = [
  { value: 'deepseek', label: 'DeepSeek V4' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'gemini', label: 'Gemini' },
  { value: 'openai_compatible', label: 'OpenAI-compatible' },
  { value: 'custom', label: 'Custom Remote API' },
] as const
export const LOCAL_AI_DISABLED_MESSAGE = 'OpsPilot 已禁用本地 AI，避免消耗本机 CPU/GPU/内存。请配置远程 API。'
const BLOCKED_LOCAL_TERMS = ['ol' + 'lama', 'v' + 'llm', 'l' + 'lama', 'local', 'offline', '本地模型', '离线模型']
const PROVIDER_TYPES: Record<typeof API_PROVIDER_OPTIONS[number], string> = {
  deepseek: 'openai-compatible',
  openai: 'openai',
  anthropic: 'anthropic',
  gemini: 'openai-compatible',
  openai_compatible: 'openai-compatible',
  custom: 'openai-compatible',
}

export function validateRemoteBaseUrl(baseUrl?: string): void {
  if (!baseUrl) return
  if (baseUrl.startsWith('file://') || baseUrl.startsWith('http+unix') || baseUrl.startsWith('unix:') || baseUrl.includes('/var/run/')) {
    throw new Error(LOCAL_AI_DISABLED_MESSAGE)
  }
  let url: URL
  try {
    url = new URL(baseUrl)
  } catch {
    throw new Error('请使用 http 或 https 远程 API 地址。')
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw new Error('请使用 http 或 https 远程 API 地址。')
  }
  const host = url.hostname.toLowerCase().replace(/^\[(.*)\]$/, '$1')
  if (host === 'localhost' || host === '0.0.0.0' || host === '::1' || host === '127.0.0.1') {
    throw new Error(LOCAL_AI_DISABLED_MESSAGE)
  }
  if (/^10\./.test(host) || /^192\.168\./.test(host) || /^172\.(1[6-9]|2\d|3[0-1])\./.test(host)) {
    throw new Error(LOCAL_AI_DISABLED_MESSAGE)
  }
}

export function assertApiOnlyProvider(provider: string): void {
  const normalized = provider.toLowerCase().replace('-', '_')
  if (BLOCKED_LOCAL_TERMS.some(word => normalized.includes(word)) || !API_PROVIDER_OPTIONS.includes(normalized as typeof API_PROVIDER_OPTIONS[number])) {
    throw new Error(LOCAL_AI_DISABLED_MESSAGE)
  }
}

export function assertRemoteModelName(model: string): void {
  const normalized = model.toLowerCase()
  if (BLOCKED_LOCAL_TERMS.some(word => normalized.includes(word))) {
    throw new Error(LOCAL_AI_DISABLED_MESSAGE)
  }
}

export function providerPatch(config: ApiProviderConfig): Record<string, unknown> {
  assertApiOnlyProvider(config.provider)
  validateRemoteBaseUrl(config.baseUrl)
  assertRemoteModelName(config.model)
  const provider = config.provider.toLowerCase().replace('-', '_') as typeof API_PROVIDER_OPTIONS[number]
  return {
    providers: {
      default: provider,
      [provider]: {
        type: config.type ?? PROVIDER_TYPES[provider],
        model: config.model,
        base_url: config.baseUrl,
        api_key_env: config.apiKeyEnv,
      },
    },
    profiles: {
      default: {
        provider,
        model: config.model,
      },
    },
  }
}

export function envCommand(envName: string, shell = 'powershell'): string {
  if (shell === 'powershell') {
    return `$env:${envName}="<your-api-key>"`
  }
  return `export ${envName}="<your-api-key>"`
}
