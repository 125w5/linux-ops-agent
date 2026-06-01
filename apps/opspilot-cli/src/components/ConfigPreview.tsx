import React from 'react'
import { Box, Text } from 'ink'
import type { ApiProviderConfig } from '../services/apiConfig.js'
import { envCommand, providerPatch } from '../services/apiConfig.js'

export function ConfigPreview({ config }: { config: ApiProviderConfig }): React.ReactElement {
  const patch = providerPatch(config)
  return <Box flexDirection="column">
    <Text color="gray">Config preview</Text>
    <Text>{JSON.stringify(patch)}</Text>
    {config.apiKeyEnv ? <Text color="yellow">{envCommand(config.apiKeyEnv)}</Text> : null}
  </Box>
}
