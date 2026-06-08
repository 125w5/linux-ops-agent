import type { AppState } from './appState.js'
import type { EngineEvent, Message, PlanStep } from './events.js'
import { clampScroll, scrollBy, scrollToLatest } from './scrollState.js'
import { messagesToVirtualLines } from '../utils/virtualLines.js'
import { normalizeResourceEvent, validateResourceEvent } from '../services/resourceEventValidator.js'

export type Action =
  | { type: 'message'; message: Message }
  | { type: 'config-flow'; flow: AppState['configFlow'] }
  | { type: 'scroll'; delta: number }
  | { type: 'scroll-latest' }
  | { type: 'viewport-height'; height: number }
  | { type: 'side-panel'; panel: AppState['activePanel'] }
  | { type: 'side-panel-next' }
  | { type: 'side-panel-visible'; visible: boolean }
  | { type: 'api-wizard-provider'; delta: number }
  | { type: 'api-wizard-step'; step: AppState['apiWizard']['step'] }
  | { type: 'engine-event'; event: EngineEvent }
  | { type: 'engine-failed'; payload: Record<string, unknown> }
  | { type: 'engine-closed'; payload: Record<string, unknown> }
  | { type: 'raw-toggle' }
  | { type: 'clear-messages' }

export function reducer(state: AppState, action: Action): AppState {
  if (action.type === 'message') {
    return appendMessage(state, action.message)
  }
  if (action.type === 'raw-toggle') {
    return { ...state, rawExpanded: !state.rawExpanded }
  }
  if (action.type === 'config-flow') {
    return { ...state, configFlow: action.flow }
  }
  if (action.type === 'scroll') {
    return { ...state, scroll: scrollBy(state.scroll, action.delta) }
  }
  if (action.type === 'scroll-latest') {
    return { ...state, scroll: scrollToLatest(state.scroll.totalLines, state.scroll.viewportHeight) }
  }
  if (action.type === 'viewport-height') {
    const totalLines = messagesToVirtualLines(state.messages).length
    const offset = state.scroll.atBottom ? clampScroll(totalLines, totalLines, action.height) : clampScroll(state.scroll.offset, totalLines, action.height)
    return { ...state, scroll: { ...state.scroll, viewportHeight: action.height, totalLines, offset, atBottom: offset >= Math.max(0, totalLines - action.height) } }
  }
  if (action.type === 'side-panel') {
    return { ...state, activePanel: action.panel, sidePanelVisible: true }
  }
  if (action.type === 'side-panel-next') {
    return { ...state, activePanel: nextPanel(state.activePanel), sidePanelVisible: true }
  }
  if (action.type === 'side-panel-visible') {
    return { ...state, sidePanelVisible: action.visible }
  }
  if (action.type === 'api-wizard-provider') {
    return { ...state, apiWizard: { ...state.apiWizard, selectedProviderIndex: clampProviderIndex(state.apiWizard.selectedProviderIndex + action.delta) } }
  }
  if (action.type === 'api-wizard-step') {
    return { ...state, apiWizard: { ...state.apiWizard, step: action.step } }
  }
  if (action.type === 'engine-failed') {
    return { ...state, status: 'EngineFailed', engine: mergeEngine(state.engine, action.payload, 'failed') }
  }
  if (action.type === 'engine-closed') {
    return { ...state, status: 'EngineClosed', engine: mergeEngine(state.engine, action.payload, 'closed') }
  }
  if (action.type === 'clear-messages') {
    return { ...state, messages: [], actions: [], plan: [], evidence: [], reportPath: '', rawExpanded: false, approvalRequest: null, configFlow: null, scroll: scrollToLatest(0, state.scroll.viewportHeight) }
  }
  const { event, payload } = action.event
  if (event === 'SessionStarted') {
    return {
      ...state,
      sessionId: String(payload.session_id ?? ''),
      target: String(payload.target ?? state.target),
      mode: String(payload.mode ?? state.mode),
      model: payload.model ? String(payload.model) : state.model,
      sandboxProfile: String(payload.sandbox_profile ?? state.sandboxProfile),
      latencyMs: Number(payload.latency_ms ?? state.latencyMs),
      status: 'idle',
      engine: mergeEngine(state.engine, payload, 'connected'),
    }
  }
  if (event === 'EngineReady') {
    return { ...state, status: event, engine: mergeEngine(state.engine, payload, 'connected') }
  }
  if (event === 'EngineFailed') {
    return { ...state, status: event, engine: mergeEngine(state.engine, payload, 'failed') }
  }
  if (event === 'TelemetryStatus') {
    return { ...state, status: event, resources: { ...state.resources, ...payload }, engine: { ...state.engine, lastResourceAt: Date.now() } }
  }
  if (event === 'TelemetryError') {
    return {
      ...state,
      status: event,
      resources: { ...state.resources, sampler_status: 'error', sampler_error: String(payload.error ?? 'telemetry error'), ...payload },
      engine: { ...state.engine, lastResourceAt: Date.now() },
    }
  }
  if (event === 'UserMessage') {
    return appendMessage({ ...state, status: event }, { role: 'user' as const, content: String(payload.content ?? '') })
  }
  if (event === 'AssistantMessage') {
    const actions = parseActions(payload.actions)
    const content = String(payload.content ?? '')
    const last = state.messages[state.messages.length - 1]
    if (last?.role === 'assistant' && last.content.startsWith('收到，正在判断任务类型')) {
      return replaceLastAssistant({ ...state, status: event, actions, responding: false }, { role: 'assistant' as const, content, actions })
    }
    if (last?.role === 'assistant' && (last.content === content || last.content.length > 0)) {
      return replaceLastAssistant({ ...state, status: event, actions, responding: false }, { role: 'assistant' as const, content, actions })
    }
    return appendMessage({ ...state, status: event, actions, responding: false }, { role: 'assistant' as const, content, actions })
  }
  if (event === 'AssistantMessageStarted') {
    const last = state.messages[state.messages.length - 1]
    if (last?.role === 'assistant' && last.content.startsWith('收到，正在判断任务类型')) {
      return replaceLastAssistant({ ...state, status: event }, { role: 'assistant' as const, content: '' })
    }
    return appendMessage({ ...state, status: event }, { role: 'assistant' as const, content: '' })
  }
  if (event === 'AssistantDelta') {
    const delta = String(payload.delta ?? '')
    const last = state.messages[state.messages.length - 1]
    if (last?.role !== 'assistant') {
      return appendMessage({ ...state, status: event }, { role: 'assistant' as const, content: delta })
    }
    return replaceLastAssistant({ ...state, status: event }, { ...last, content: `${last.content}${delta}` })
  }
  if (event === 'AssistantMessageDone') {
    return { ...state, status: event }
  }
  if (event === 'PlanCreated') {
    const steps = Array.isArray(payload.steps) ? payload.steps as PlanStep[] : []
    return { ...state, status: event, plan: steps.map(step => ({ ...step, status: 'pending' })) }
  }
  if (event === 'ToolStarted') {
    const stepId = String(payload.step_id ?? payload.command ?? 'tool')
    const command = String(payload.command ?? payload.tool_name ?? stepId)
    return appendMessage({ ...state, status: event, plan: updateStep(state.plan, stepId, 'running') }, { role: 'tool', content: `[running] ${command}` })
  }
  if (event === 'ToolFinished') {
    const status = payload.status === 0 ? 'done' : `rc=${String(payload.status)}`
    const stepId = String(payload.step_id ?? payload.command ?? 'tool')
    const command = String(payload.command ?? stepId)
    return appendMessage({ ...state, status: event, plan: updateStep(state.plan, stepId, status) }, { role: 'tool', content: `[${status}] ${command}` })
  }
  if (event === 'EvidenceAdded') {
    const items = Array.isArray(payload.items) ? payload.items : []
    return { ...state, status: event, evidence: items.map(item => String((item as Record<string, unknown>).content ?? '')) }
  }
  if (event === 'ResourceUpdated') {
    const validation = validateResourceEvent(payload)
    const normalized = normalizeResourceEvent(payload)
    const resources = { ...state.resources, ...normalized }
    const session = readObject(payload.session)
    const trace = readObject(session.latency_trace)
    return {
      ...state,
      status: event,
      resources,
      engine: { ...state.engine, lastResourceAt: Date.now() },
      resourceHistory: [...state.resourceHistory, resources].slice(-30),
      sandboxProfile: String(session.sandbox_profile ?? state.sandboxProfile),
      latencyMs: Number(session.latency_ms ?? state.latencyMs),
      apiCalls: Number(session.api_calls ?? state.apiCalls),
      apiLatencyMs: Number(session.api_latency_ms ?? state.apiLatencyMs),
      fallbackReason: String(session.fallback_reason ?? state.fallbackReason),
      responding: Boolean(session.responding ?? state.responding),
      latencyTrace: Object.keys(trace).length ? trace : state.latencyTrace,
      resourceSchemaError: validation.ok ? '' : validation.errors.join('; '),
      estimatedTokens: Number(session.estimated_tokens ?? state.estimatedTokens),
      commandsExecuted: Number(session.commands_executed ?? state.commandsExecuted),
      outputBytes: Number(session.output_bytes ?? state.outputBytes),
    }
  }
  if (event === 'TelemetryDoctor') {
    return { ...state, status: event, telemetryDoctor: readObject(payload.doctor), activePanel: 'Resources', sidePanelVisible: true }
  }
  if (event === 'LatencyTrace') {
    return { ...state, status: event, latencyTrace: readObject(payload.trace), activePanel: 'Raw', sidePanelVisible: true }
  }
  if (event === 'ApprovalRequired') {
    return {
      ...state,
      status: event,
      approvalPending: true,
      approvalRequest: {
        action: String(payload.action ?? 'command'),
        command: String(payload.command ?? ''),
        risk: String(payload.risk_level ?? payload.risk ?? state.risk),
        sandboxProfile: String(payload.sandbox_profile ?? state.sandboxProfile),
        reason: String(payload.reason ?? 'Confirmation required'),
        target: String(payload.target ?? state.target),
      },
      activePanel: 'Approval',
      sidePanelVisible: true,
    }
  }
  if (event === 'ApprovalResolved') {
    return { ...state, status: event, approvalPending: false, approvalRequest: null }
  }
  if (event === 'ReportWritten') {
    return { ...state, status: event, reportPath: String(payload.markdown_path ?? '') }
  }
  if (event === 'SessionEnded') {
    return { ...state, status: event, risk: String(payload.risk_level ?? state.risk) }
  }
  return { ...state, status: event }
}

const PANELS: AppState['activePanel'][] = ['Task', 'Evidence', 'Resources', 'Raw', 'Report', 'Config', 'Process', 'Approval']

function appendMessage(state: AppState, message: Message): AppState {
  const messages = [...state.messages, message].slice(-200)
  return withUpdatedScroll({ ...state, messages })
}

function replaceLastAssistant(state: AppState, message: Message): AppState {
  const messages = [...state.messages.slice(0, -1), message].slice(-200)
  return withUpdatedScroll({ ...state, messages })
}

function withUpdatedScroll(state: AppState): AppState {
  const totalLines = messagesToVirtualLines(state.messages).length
  const offset = state.scroll.atBottom ? clampScroll(totalLines, totalLines, state.scroll.viewportHeight) : clampScroll(state.scroll.offset, totalLines, state.scroll.viewportHeight)
  return {
    ...state,
    scroll: {
      ...state.scroll,
      totalLines,
      offset,
      atBottom: offset >= Math.max(0, totalLines - state.scroll.viewportHeight),
    },
  }
}

function nextPanel(panel: AppState['activePanel']): AppState['activePanel'] {
  return PANELS[(PANELS.indexOf(panel) + 1) % PANELS.length]
}

function clampProviderIndex(value: number): number {
  return Math.max(0, Math.min(5, value))
}

function updateStep(plan: PlanStep[], id: string, status: string): PlanStep[] {
  return plan.map(step => step.id === id ? { ...step, status } : step)
}

function parseActions(value: unknown): AppState['actions'] {
  if (!Array.isArray(value)) {
    return []
  }
  return value
    .map(item => item && typeof item === 'object' ? item as Record<string, unknown> : {})
    .filter(item => item.label && item.command)
    .map(item => ({ label: String(item.label), command: String(item.command) }))
}

function readObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {}
}

function mergeEngine(engine: AppState['engine'], payload: Record<string, unknown>, status: AppState['engine']['status']): AppState['engine'] {
  const stderr = Array.isArray(payload.stderr) ? payload.stderr.map(String) : engine.stderr
  return {
    ...engine,
    status,
    pid: typeof payload.pid === 'number' ? payload.pid : engine.pid,
    cwd: payload.cwd ? String(payload.cwd) : engine.cwd,
    python: payload.python_executable ? String(payload.python_executable) : payload.python ? String(payload.python) : engine.python,
    stderr,
    error: payload.error ? String(payload.error) : payload.message ? String(payload.message) : engine.error,
  }
}
