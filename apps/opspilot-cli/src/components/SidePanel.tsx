import React from 'react'
import { Box, Text } from 'ink'
import type { AppState } from '../state/appState.js'
import { ApprovalCard } from './ApprovalCard.js'
import { ProcessActionPanel } from './ProcessActionPanel.js'
import { SandboxProfileCard } from './SandboxProfileCard.js'
import { ApiConfigWizard } from '../screens/ApiConfigWizard.js'
import type { ProcessRow } from './ProcessCard.js'
import { MonitorPane } from './MonitorPane.js'
import { SidePanelTabs } from './SidePanelTabs.js'
import { TelemetryDoctorPanel } from './TelemetryDoctorPanel.js'
import { LatencyPanel } from './LatencyPanel.js'

export function SidePanel({ state, height = 12, width = 48 }: { state: AppState; height?: number; width?: number }): React.ReactElement {
  const system = readObject(state.resources.system)
  const topCpu = readRows(state.resources.top_cpu_processes)
  const topMemory = readRows(state.resources.top_memory_processes)

  return <Box flexDirection="column" height={height} width={width} overflow="hidden">
    <SidePanelTabs active={state.activePanel} width={width} />
    {state.activePanel === 'Task' ? <TaskPanel state={state} system={system} /> : null}
    {state.activePanel === 'Evidence' ? <EvidencePanel state={state} /> : null}
    {state.activePanel === 'Resources' ? <Box flexDirection="column"><MonitorPane resources={state.resources} history={state.resourceHistory} /><TelemetryDoctorPanel doctor={state.telemetryDoctor} /></Box> : null}
    {state.activePanel === 'Raw' ? <LatencyPanel trace={state.latencyTrace} /> : null}
    {state.activePanel === 'Report' ? <Text>{state.reportPath ? `Report ${state.reportPath}` : 'No report yet. Run /run first.'}</Text> : null}
    {state.activePanel === 'Config' ? (state.configFlow ? <ApiConfigWizard config={state.configFlow} wizard={state.apiWizard} /> : <Text color="gray">Use /config api to start the API wizard.</Text>) : null}
    {state.activePanel === 'Process' ? <ProcessPanel topCpu={topCpu} topMemory={topMemory} /> : null}
    {state.activePanel === 'Approval' ? (state.approvalRequest ? <ApprovalCard {...state.approvalRequest} /> : <Text color="gray">No approval is pending.</Text>) : null}
  </Box>
}

function TaskPanel({ state, system }: { state: AppState; system: Record<string, unknown> }): React.ReactElement {
  return <Box flexDirection="column">
    <SandboxProfileCard name={state.sandboxProfile} description={sandboxDescription(state.sandboxProfile)} />
    <Box flexDirection="column" borderStyle="single" borderColor="gray" paddingX={1}>
      <Text color="gray">Current Task</Text>
      <Text>{truncate(state.plan[0]?.name ?? 'waiting for the next command', 42)}</Text>
      <Text color="gray">Latency {state.latencyMs}ms | API {state.apiCalls} | Tokens~{state.estimatedTokens}</Text>
      <Text color="gray">API latency {state.apiLatencyMs}ms | fallback {state.fallbackReason || 'none'}</Text>
      <Text color="gray">CPU {String(system.cpu_percent ?? 'n/a')}% | MEM {String(system.memory_percent ?? 'n/a')}%</Text>
      {state.resourceSchemaError ? <Text color="red">Resource schema: {truncate(state.resourceSchemaError, 42)}</Text> : null}
    </Box>
  </Box>
}

function EvidencePanel({ state }: { state: AppState }): React.ReactElement {
  return <Box flexDirection="column" borderStyle="single" borderColor="gray" paddingX={1}>
    <Text color="gray">Evidence</Text>
    {state.evidence.length ? state.evidence.slice(0, 6).map((item, index) => <Text key={index}>{truncate(item, 64)}</Text>) : <Text color="gray">waiting for evidence</Text>}
  </Box>
}

function ProcessPanel({ topCpu, topMemory }: { topCpu: ProcessRow[]; topMemory: ProcessRow[] }): React.ReactElement {
  return <Box flexDirection="column">
    <ProcessActionPanel title="Top CPU" rows={topCpu} />
    <ProcessActionPanel title="Top Memory" rows={topMemory} />
    {!topCpu.length && !topMemory.length ? <Text color="gray">Use /process to refresh process cards.</Text> : null}
  </Box>
}

function sandboxDescription(name: string): string {
  if (name === 'ops-read') return 'Read configs, logs, docker state, and validation commands.'
  if (name === 'lab-write') return 'Low-risk writes only inside sandbox workflows.'
  if (name === 'admin-confirm') return 'Ask before real low-risk operations.'
  return 'Read-only observation commands.'
}

function readObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {}
}

function readRows(value: unknown): ProcessRow[] {
  const rows = Array.isArray(value) ? value.filter(item => item && typeof item === 'object') as Array<Record<string, unknown>> : []
  return rows
    .filter(item => item.pid !== undefined)
    .map(item => ({
      pid: String(item.pid),
      name: String(item.name ?? '?'),
      cpu_percent: Number(item.normalized_cpu_percent ?? item.cpu_percent ?? 0),
      raw_cpu_percent: Number(item.raw_cpu_percent ?? item.cpu_percent ?? 0),
      memory_percent: Number(item.memory_percent ?? 0),
      memory_mb: item.memory_mb === undefined ? bytesToMb(item.memory_bytes) : Number(item.memory_mb),
    }))
}

function bytesToMb(value: unknown): number | undefined {
  return typeof value === 'number' ? value / 1024 / 1024 : undefined
}

function truncate(value: string, maxLength: number): string {
  return value.length <= maxLength ? value : `${value.slice(0, Math.max(0, maxLength - 3))}...`
}
