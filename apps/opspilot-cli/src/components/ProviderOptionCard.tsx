import React from 'react'
import { Box, Text } from 'ink'

export function ProviderOptionCard({
  index,
  label,
  value,
  selected,
}: {
  index: number
  label: string
  value: string
  selected: boolean
}): React.ReactElement {
  return <Box>
    <Text color={selected ? 'cyan' : 'gray'}>{selected ? '>' : ' '} [{index}] {label}</Text>
    <Text color="gray"> /config api {value}</Text>
  </Box>
}
