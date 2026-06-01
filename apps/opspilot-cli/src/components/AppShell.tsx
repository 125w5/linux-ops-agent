import React from 'react'
import { Box, Text } from 'ink'
import type { AppState } from '../state/appState.js'
import type { PlanStep } from '../state/events.js'
import { InputBox } from './InputBox.js'

const WIDTH = 78

export function AppShell({ state, input }: { state: AppState; input: string }): React.ReactElement {
  return <Box flexDirection="column">
    <Box borderStyle="round" borderColor="cyan" flexDirection="column" width={WIDTH}>
      <Box paddingX={1} flexDirection="column">
        <Text color="cyan" bold>OpsPilot-Linux</Text>
        <Text>{statusText(state)}</Text>
      </Box>

      <Section title="Monitor">
        <Text>{monitorText(state)}</Text>
      </Section>

      <Section title="Conversation">
        {conversationLines(state).map((line, index) => (
          <Text key={index}>
            <Text color={line.role === 'assistant' ? 'cyan' : line.role === 'user' ? 'green' : 'yellow'}>
              {line.role.padEnd(9)}
            </Text>
            {'  '}
            {line.content}
          </Text>
        ))}
      </Section>

      <Box flexDirection="row">
        <Box flexDirection="column" width={38}>
          <Section title="Plan / Tools">
            {planLines(state.plan).map((line, index) => <Text key={index}>{line}</Text>)}
          </Section>
        </Box>
        <Box flexDirection="column" width={38}>
          <Section title="Evidence / Report">
            {evidenceLines(state).map((line, index) => <Text key={index}>{line}</Text>)}
          </Section>
        </Box>
      </Box>

      <Box flexDirection="row">
        <Box flexDirection="column" width={38}>
          <Section title={`Raw ${state.rawExpanded ? 'expanded' : 'folded'}`}>
            <Text>{state.rawExpanded ? 'raw stream visible when engine provides it' : 'use /raw to expand'}</Text>
          </Section>
        </Box>
        <Box flexDirection="column" width={38}>
          <Section title="Resources">
            <Text>{resourceText(state)}</Text>
          </Section>
        </Box>
      </Box>
    </Box>
    <InputBox value={input} />
  </Box>
}

function Section({ title, children }: { title: string; children: React.ReactNode }): React.ReactElement {
  return <Box borderStyle="single" borderColor="gray" flexDirection="column" paddingX={1}>
    <Text color="gray">{title}</Text>
    {children}
  </Box>
}

function statusText(state: AppState): string {
  return `session=${shortSession(state.sessionId)}  mode=${state.mode}  model=${state.model || 'default'}  risk=${state.risk}`
}

function monitorText(state: AppState): string {
  const system = readObject(state.resources.system)
  const disk = readObject(state.resources.disk)
  const cpu = formatPercent(system.cpu_percent)
  const memory = formatPercent(system.memory_percent)
  const diskPercent = formatPercent(disk.percent ?? disk.disk_percent)
  return `CPU ${cpu}   MEM ${memory}   DISK ${diskPercent}   provider=mock   status=${state.status}`
}

function conversationLines(state: AppState): Array<{ role: string; content: string }> {
  const lines = state.messages.slice(-8).map(message => ({
    role: message.role,
    content: message.content.replace(/\n/g, '  '),
  }))
  return lines.length ? lines : [{ role: 'assistant', content: '你好，我是 OpsPilot。描述故障，或输入 /help。' }]
}

function planLines(plan: PlanStep[]): string[] {
  if (!plan.length) {
    return ['waiting for your description']
  }
  return plan.slice(0, 6).map((step, index) => `${index + 1} ${(step.status ?? 'pending').padEnd(8)} ${step.id}`)
}

function evidenceLines(state: AppState): string[] {
  const evidence = state.evidence.slice(0, 4)
  if (!evidence.length && !state.reportPath) {
    return ['waiting']
  }
  const lines = evidence.length ? evidence.map(item => trim(item, 34)) : ['waiting']
  if (state.reportPath) {
    lines.push(`report ${trim(state.reportPath, 28)}`)
  }
  return lines
}

function resourceText(state: AppState): string {
  const commands = readObject(state.resources.commands)
  const ai = readObject(state.resources.ai)
  const output = readObject(state.resources.output)
  return `commands=${commands.executed ?? commands.count ?? 0} ai=${ai.calls ?? ai.count ?? 0} out=${output.kb ?? output.bytes ?? 0}KB`
}

function readObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {}
}

function formatPercent(value: unknown): string {
  if (typeof value === 'number') {
    return `${value.toFixed(1)}%`
  }
  return '--'
}

function shortSession(sessionId: string): string {
  return sessionId ? sessionId.slice(0, 8) : 'pending'
}

function trim(value: string, max: number): string {
  return value.length > max ? `${value.slice(0, max - 1)}…` : value
}
