import React from 'react'
import { Box, Text } from 'ink'
import { findCommands } from '../commands/registry.js'

export function CommandPalette({ prefix = '/' }: { prefix?: string }): React.ReactElement {
  return <Box flexDirection="column"><Text color="cyan">Commands</Text>{findCommands(prefix).map(command => <Text key={command.name}>{command.name} {command.description}</Text>)}</Box>
}
