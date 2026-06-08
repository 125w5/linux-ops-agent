import React from 'react'
import { Box, Text } from 'ink'

export function SandboxProfileCard({
  name,
  description,
  allow,
  ask,
  deny,
  examples,
}: {
  name: string
  description: string
  allow?: string[]
  ask?: string[]
  deny?: string[]
  examples?: string[]
}): React.ReactElement {
  return <Box flexDirection="column" borderStyle="single" borderColor="gray" paddingX={1}>
    <Text color="gray">Sandbox</Text>
    <Text bold>{name}</Text>
    <Text>{description}</Text>
    {allow?.length ? <Text color="green">allow: {allow.join(', ')}</Text> : null}
    {ask?.length ? <Text color="yellow">ask: {ask.join(', ')}</Text> : null}
    {deny?.length ? <Text color="red">deny: {deny.join(', ')}</Text> : null}
    {examples?.length ? <Text color="gray">examples: {examples.join(' | ')}</Text> : null}
  </Box>
}
