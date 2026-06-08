import React from 'react'
import { Box, Text } from 'ink'

export function ToolSummaryMessage({ name, status }: { name: string; status: string }): React.ReactElement {
  return <Box>
    <Box marginRight={1}>
      <Text color="yellow">tool</Text>
    </Box>
    <Box marginRight={1}>
      <Text>{name}</Text>
    </Box>
    <Text color="gray">{status}</Text>
  </Box>
}
