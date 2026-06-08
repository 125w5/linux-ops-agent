import React from 'react'
import { Box, Text } from 'ink'
import type { AppState } from '../state/appState.js'

export function EngineErrorPanel({ engine }: { engine: AppState['engine'] }): React.ReactElement | null {
  if (engine.status !== 'failed' && engine.status !== 'closed') {
    return null
  }
  return <Box flexDirection="column" borderStyle="single" borderColor="red" paddingX={1}>
    <Text color="red">Engine {engine.status}</Text>
    <Text>cwd: {engine.cwd ?? 'unknown'}</Text>
    <Text>pid: {String(engine.pid ?? 'none')}</Text>
    <Text>error: {engine.error ?? 'unknown'}</Text>
    <Text color="gray">stderr:</Text>
    {engine.stderr.length ? engine.stderr.slice(-5).map((line, index) => <Text key={index}>{truncate(line, 76)}</Text>) : <Text color="gray">no stderr captured</Text>}
  </Box>
}

function truncate(value: string, maxLength: number): string {
  return value.length <= maxLength ? value : `${value.slice(0, Math.max(0, maxLength - 3))}...`
}
