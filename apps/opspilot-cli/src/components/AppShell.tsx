import React from 'react'
import { Box, Text } from 'ink'
import type { AppState } from '../state/appState.js'
import type { Viewport } from '../layout/viewport.js'
import { currentViewport } from '../layout/viewport.js'
import { ActionBar } from './ActionBar.js'
import { ConversationPane } from './ConversationPane.js'
import { InputBox } from './InputBox.js'
import { MonitorPane } from './MonitorPane.js'
import { SidePanel } from './SidePanel.js'
import { WorkbenchLayout } from './WorkbenchLayout.js'
import { EngineErrorPanel } from './EngineErrorPanel.js'

export function AppShell({
  state,
  input,
  selectedActionIndex,
  searchTerm,
  viewport = currentViewport(),
}: {
  state: AppState
  input: string
  selectedActionIndex: number
  searchTerm: string
  viewport?: Viewport
}): React.ReactElement {
  const sideVisible = viewport.showSidePanel && state.sidePanelVisible
  const conversationWidth = sideVisible ? viewport.conversationWidth : viewport.width - 2

  return <WorkbenchLayout
    viewport={viewport}
    header={<Header state={state} />}
    monitor={<Box paddingX={1} height={viewport.monitorHeight} overflow="hidden"><MonitorPane resources={state.resources} history={state.resourceHistory} compact /></Box>}
    body={<Box height={viewport.bodyHeight} paddingX={1}>
      <Box flexDirection="column" width={conversationWidth} height={viewport.bodyHeight}>
        <EngineErrorPanel engine={state.engine} />
        <ConversationPane messages={state.messages} searchTerm={searchTerm} scroll={state.scroll} height={viewport.bodyHeight} width={conversationWidth} />
      </Box>
      {sideVisible ? <Box flexDirection="column" width={viewport.sideWidth} height={viewport.bodyHeight} marginLeft={1}>
        <SidePanel state={state} height={viewport.bodyHeight} width={viewport.sideWidth} />
      </Box> : null}
    </Box>}
    actions={<Box paddingX={1} height={viewport.actionHeight}><ActionBar actions={state.actions} selectedIndex={selectedActionIndex} /></Box>}
    input={<Box paddingX={1}><InputBox value={input} /></Box>}
  />
}

function Header({ state }: { state: AppState }): React.ReactElement {
  return <Box paddingX={1}>
    <Box marginRight={1}>
      <Text color="cyan" bold>OpsPilot-Linux</Text>
    </Box>
    <Text>{statusText(state)}</Text>
  </Box>
}

function statusText(state: AppState): string {
  return `engine=${state.engine.status} session=${shortSession(state.sessionId)} mode=${state.mode} sandbox=${state.sandboxProfile} panel=${state.activePanel} model=${state.model || 'default'}`
}

function shortSession(sessionId: string): string {
  return sessionId ? sessionId.slice(0, 8) : 'pending'
}
