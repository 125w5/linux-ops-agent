import React from 'react'
import { Box, Text } from 'ink'

export function FormSelect({ label, value, options }: { label: string; value: string; options: string[] }): React.ReactElement {
  return <Box flexDirection="column">
    <Text color="cyan">{label}: {value || 'not set'}</Text>
    <Text color="gray">{options.map(option => option === value ? `[${option}]` : option).join('  ')}</Text>
  </Box>
}
