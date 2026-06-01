import React from 'react'
import { Text } from 'ink'
import { commandHelp } from '../commands/registry.js'

export function HelpScreen(): React.ReactElement {
  return <Text>{commandHelp('/')}</Text>
}
