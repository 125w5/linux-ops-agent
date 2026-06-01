import React from 'react'
import { Box, Text } from 'ink'

export type ModelDoctorRow = {
  provider: string
  status: string
  model: string
  note: string
}

export function ModelScreen(): React.ReactElement {
  return <Text>Model: /model list, /model doctor, /model use provider:model</Text>
}

export function ModelDoctorVisual({ rows }: { rows: ModelDoctorRow[] }): React.ReactElement {
  return <Box flexDirection="column">
    <Text color="gray">provider           status       model                 note</Text>
    {rows.map(row => <Text key={row.provider}>{row.provider.padEnd(18)} {row.status.padEnd(12)} {row.model.padEnd(20)} {row.note}</Text>)}
  </Box>
}
