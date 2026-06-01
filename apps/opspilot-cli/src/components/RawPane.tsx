import React from 'react'
import { Text } from 'ink'

export function RawPane({ expanded }: { expanded: boolean }): React.ReactElement {
  return <Text color="cyan">Raw {expanded ? 'expanded' : 'folded'}</Text>
}
