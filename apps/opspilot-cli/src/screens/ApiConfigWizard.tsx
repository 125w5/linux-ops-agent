import React from 'react'
import { Box, Text } from 'ink'
import { ConfigPreview } from '../components/ConfigPreview.js'
import { FormInput } from '../components/FormInput.js'
import { FormSelect } from '../components/FormSelect.js'
import { API_PROVIDER_CHOICES, type ApiProviderConfig } from '../services/apiConfig.js'

export function ApiConfigWizard({ config }: { config: ApiProviderConfig }): React.ReactElement {
  return <Box flexDirection="column">
    <Text color="cyan">API setup wizard</Text>
    <FormSelect label="Provider" value={config.provider} options={[...API_PROVIDER_CHOICES]} />
    <FormInput label="Base URL" value={config.baseUrl} placeholder="https://api.example.com/v1" />
    <FormInput label="Model" value={config.model} placeholder="model name" />
    <FormInput label="API key env" value={config.apiKeyEnv} placeholder="OPENAI_API_KEY" />
    <ConfigPreview config={config} />
  </Box>
}
