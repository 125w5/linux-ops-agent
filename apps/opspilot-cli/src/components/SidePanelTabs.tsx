import React from 'react'
import { Box, Text } from 'ink'
import type { SidePanelName } from '../state/appState.js'

export const SIDE_PANELS: SidePanelName[] = ['Task', 'Evidence', 'Resources', 'Raw', 'Report', 'Config', 'Process', 'Approval']

export function SidePanelTabs({ active, width = 48 }: { active: SidePanelName; width?: number }): React.ReactElement {
  if (width < 58) {
    return <Box height={1} overflow="hidden">
      <Text color="cyan">Panel: {active}</Text>
      <Text color="gray">  (Tab/F2-F8)</Text>
    </Box>
  }
  const visible = SIDE_PANELS.slice(0, 5)
  return <Box height={1} overflow="hidden">
    {visible.map(panel => (
      <Box key={panel} marginRight={1}>
        <Text color={panel === active ? 'black' : 'gray'} backgroundColor={panel === active ? 'cyan' : undefined}>
          [{panel}]
        </Text>
      </Box>
    ))}
  </Box>
}
