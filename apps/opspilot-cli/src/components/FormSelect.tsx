import React from 'react'
import { Box, Text } from 'ink'

export type FormSelectOption = string | { value: string; label: string }

function optionValue(option: FormSelectOption): string {
  return typeof option === 'string' ? option : option.value
}

function optionLabel(option: FormSelectOption): string {
  return typeof option === 'string' ? option : option.label
}

export function FormSelect({ label, value, options }: { label: string; value: string; options: FormSelectOption[] }): React.ReactElement {
  return <Box flexDirection="column">
    <Text color="cyan">{label}: {value || 'not set'}</Text>
    <Text color="gray">{options.map(option => optionValue(option) === value ? `[${optionLabel(option)}]` : optionLabel(option)).join('  ')}</Text>
  </Box>
}
