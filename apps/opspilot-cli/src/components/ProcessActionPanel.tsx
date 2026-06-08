import React from 'react'
import { Box, Text } from 'ink'
import type { ProcessRow } from './ProcessCard.js'
import { ProcessCard } from './ProcessCard.js'

export function ProcessActionPanel({ title, rows }: { title: string; rows: ProcessRow[] }): React.ReactElement | null {
  if (!rows.length) {
    return null
  }
  return <Box flexDirection="column">
    <Text color="gray">{title}</Text>
    {rows.slice(0, 3).map(row => <ProcessCard key={`${row.pid}-${row.name}`} process={row} />)}
  </Box>
}
