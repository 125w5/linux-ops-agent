import React from 'react'
import { Box } from 'ink'
import type { Viewport } from '../layout/viewport.js'

export function WorkbenchLayout({
  viewport,
  header,
  monitor,
  body,
  actions,
  input,
}: {
  viewport: Viewport
  header: React.ReactNode
  monitor: React.ReactNode
  body: React.ReactNode
  actions: React.ReactNode
  input: React.ReactNode
}): React.ReactElement {
  return <Box flexDirection="column" width={viewport.width} height={viewport.height}>
    <Box height={viewport.headerHeight} flexShrink={0} overflow="hidden">{header}</Box>
    <Box height={viewport.monitorHeight} flexShrink={0} overflow="hidden">{monitor}</Box>
    <Box height={viewport.bodyHeight} flexShrink={0} overflow="hidden">{body}</Box>
    <Box height={viewport.actionHeight} flexShrink={0} overflow="hidden">{actions}</Box>
    <Box height={viewport.inputHeight} flexShrink={0} overflow="hidden">{input}</Box>
  </Box>
}
