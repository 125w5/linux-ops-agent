import React from 'react'
import { Box, Text } from 'ink'
import { ConfigPreview } from '../components/ConfigPreview.js'
import { FormInput } from '../components/FormInput.js'
import { FormSelect } from '../components/FormSelect.js'
import { ProviderOptionCard } from '../components/ProviderOptionCard.js'
import { API_PROVIDER_CHOICES, type ApiProviderConfig } from '../services/apiConfig.js'

export function ApiConfigWizard({
  config,
  wizard,
}: {
  config: ApiProviderConfig
  wizard?: { step: string; selectedProviderIndex: number; error?: string }
}): React.ReactElement {
  const selectedProvider = API_PROVIDER_CHOICES[wizard?.selectedProviderIndex ?? API_PROVIDER_CHOICES.findIndex(choice => choice.value === config.provider)]?.value ?? config.provider
  return <Box flexDirection="column">
    <Text color="cyan">API setup wizard - step {wizard?.step ?? 'provider'}</Text>
    <FormSelect label="Provider" value={config.provider} options={[...API_PROVIDER_CHOICES]} />
    <Box flexDirection="column">
      {API_PROVIDER_CHOICES.map((choice, index) => (
        <ProviderOptionCard key={choice.value} index={index + 1} label={choice.label} value={choice.value} selected={choice.value === selectedProvider} />
      ))}
    </Box>
    <FormInput label="Base URL" value={config.baseUrl} placeholder="https://api.example.com/v1" />
    <FormInput label="Model" value={config.model} placeholder="model name" />
    <FormInput label="API key env" value={config.apiKeyEnv} placeholder="OPENAI_API_KEY" />
    <ConfigPreview config={config} />
    {wizard?.error ? <Text color="red">{wizard.error}</Text> : null}
    <Text color="gray">Save: /config api save. Real API keys stay in env vars only.</Text>
  </Box>
}
