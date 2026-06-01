import React from 'react'
import { Text } from 'ink'

export function FormInput({ label, value, placeholder }: { label: string; value?: string; placeholder?: string }): React.ReactElement {
  return <Text>
    <Text color="cyan">{label}: </Text>
    {value || <Text color="gray">{placeholder ?? 'not set'}</Text>}
  </Text>
}
