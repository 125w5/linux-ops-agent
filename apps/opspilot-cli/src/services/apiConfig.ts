export type ApiProviderConfig = {
  provider: string
  model: string
  baseUrl?: string
  apiKeyEnv?: string
}

export function providerPatch(config: ApiProviderConfig): Record<string, unknown> {
  return {
    providers: {
      default: config.provider,
      [config.provider]: {
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
