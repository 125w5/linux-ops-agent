import type { AppState } from './appState.js'
import type { EngineEvent, Message, PlanStep } from './events.js'

export type Action =
  | { type: 'message'; message: Message }
  | { type: 'engine-event'; event: EngineEvent }
  | { type: 'raw-toggle' }

export function reducer(state: AppState, action: Action): AppState {
  if (action.type === 'message') {
    return { ...state, messages: [...state.messages, action.message].slice(-200) }
  }
  if (action.type === 'raw-toggle') {
    return { ...state, rawExpanded: !state.rawExpanded }
  }
  const { event, payload } = action.event
  if (event === 'SessionStarted') {
    return {
      ...state,
      sessionId: String(payload.session_id ?? ''),
      target: String(payload.target ?? state.target),
      mode: String(payload.mode ?? state.mode),
      model: payload.model ? String(payload.model) : state.model,
      status: 'idle',
    }
  }
  if (event === 'UserMessage') {
    return { ...state, status: event, messages: [...state.messages, { role: 'user' as const, content: String(payload.content ?? '') }].slice(-200) }
  }
  if (event === 'AssistantMessage') {
    return { ...state, status: event, messages: [...state.messages, { role: 'assistant' as const, content: String(payload.content ?? '') }].slice(-200) }
  }
  if (event === 'PlanCreated') {
    const steps = Array.isArray(payload.steps) ? payload.steps as PlanStep[] : []
    return { ...state, status: event, plan: steps.map(step => ({ ...step, status: 'pending' })) }
  }
  if (event === 'ToolStarted') {
    return { ...state, status: event, plan: updateStep(state.plan, String(payload.step_id ?? ''), 'running') }
  }
  if (event === 'ToolFinished') {
    const status = payload.status === 0 ? 'done' : `rc=${String(payload.status)}`
    return { ...state, status: event, plan: updateStep(state.plan, String(payload.step_id ?? ''), status) }
  }
  if (event === 'EvidenceAdded') {
    const items = Array.isArray(payload.items) ? payload.items : []
    return { ...state, status: event, evidence: items.map(item => String((item as Record<string, unknown>).content ?? '')) }
  }
  if (event === 'ResourceUpdated') {
    return { ...state, status: event, resources: { ...state.resources, ...payload } }
  }
  if (event === 'ApprovalRequired') {
    return { ...state, status: event, approvalPending: true }
  }
  if (event === 'ApprovalResolved') {
    return { ...state, status: event, approvalPending: false }
  }
  if (event === 'ReportWritten') {
    return { ...state, status: event, reportPath: String(payload.markdown_path ?? '') }
  }
  if (event === 'SessionEnded') {
    return { ...state, status: event, risk: String(payload.risk_level ?? state.risk) }
  }
  return { ...state, status: event }
}

function updateStep(plan: PlanStep[], id: string, status: string): PlanStep[] {
  return plan.map(step => step.id === id ? { ...step, status } : step)
}
