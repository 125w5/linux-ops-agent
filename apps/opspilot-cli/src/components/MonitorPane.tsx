import React from 'react'
import { Box, Text } from 'ink'

export function MonitorPane({ resources }: { resources: Record<string, unknown> }): React.ReactElement {
  const system = resources.system as Record<string, unknown> | undefined
  return <Box flexDirection="column"><Text color="cyan">Monitor</Text><Text>CPU {String(system?.cpu_percent ?? 'n/a')} | Mem {String(system?.memory_percent ?? 'n/a')}</Text></Box>
}
