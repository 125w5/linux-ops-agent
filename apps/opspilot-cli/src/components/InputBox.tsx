import React from 'react'
import { Box, Text } from 'ink'

export function InputBox({ value }: { value: string }): React.ReactElement {
  return <Box marginTop={1}>
    <Text color="green">diag&gt; </Text>
    <Text>{value}</Text>
    <Text color="green">█</Text>
  </Box>
}
