import React from 'react'
import { Box, Text } from 'ink'
import { ProcessActionPanel } from '../components/ProcessActionPanel.js'
import type { ProcessRow } from '../components/ProcessCard.js'

export function ProcessScreen({
  topCpu,
  topMemory,
}: {
  topCpu: ProcessRow[]
  topMemory: ProcessRow[]
}): React.ReactElement {
  return <Box flexDirection="column">
    <Text color="cyan" bold>Process Actions</Text>
    <ProcessActionPanel title="Top CPU" rows={topCpu} />
    <ProcessActionPanel title="Top Memory" rows={topMemory} />
  </Box>
}
