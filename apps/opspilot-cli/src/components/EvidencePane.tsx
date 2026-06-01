import React from 'react'
import { Box, Text } from 'ink'

export function EvidencePane({ evidence }: { evidence: string[] }): React.ReactElement {
  return <Box flexDirection="column"><Text color="cyan">Evidence</Text>{evidence.length === 0 ? <Text>waiting</Text> : evidence.map((item, index) => <Text key={index}>- {item}</Text>)}</Box>
}
