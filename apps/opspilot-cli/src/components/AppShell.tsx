import React from 'react'
import { Box } from 'ink'
import type { AppState } from '../state/appState.js'
import { ApprovalDialog } from './ApprovalDialog.js'
import { CommandPalette } from './CommandPalette.js'
import { ConversationPane } from './ConversationPane.js'
import { EvidencePane } from './EvidencePane.js'
import { InputBox } from './InputBox.js'
import { MonitorPane } from './MonitorPane.js'
import { PlanPane } from './PlanPane.js'
import { RawPane } from './RawPane.js'
import { ReportPane } from './ReportPane.js'
import { StatusLine } from './StatusLine.js'
import { ToolCallList } from './ToolCallList.js'

export function AppShell({ state }: { state: AppState }): React.ReactElement {
  return <Box flexDirection="column">
    <StatusLine state={state} />
    <ConversationPane messages={state.messages} />
    <MonitorPane resources={state.resources} />
    <PlanPane plan={state.plan} />
    <ToolCallList plan={state.plan} />
    <EvidencePane evidence={state.evidence} />
    <RawPane expanded={state.rawExpanded} />
    <ReportPane path={state.reportPath} />
    <ApprovalDialog pending={state.approvalPending} />
    <CommandPalette />
    <InputBox />
  </Box>
}
