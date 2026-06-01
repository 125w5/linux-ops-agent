export type ApiProviderConfig = {
  provider: string
  type?: string
  model: string
  baseUrl?: string
  apiKeyEnv?: string
}

export function providerPatch(config: ApiProviderConfig): Record<string, unknown> {
  return {
    providers: {
      default: config.provider,
      [config.provider]: {
        type: config.type ?? 'openai-compatible',
        model: config.model,
        base_url: config.baseUrl,
        api_key_env: config.apiKeyEnv,
      },
    },
    profiles: {
      default: {
        provider: config.provider,
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
