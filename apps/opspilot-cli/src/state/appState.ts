import type { Message, PlanStep } from './events.js'

export type AppState = {
  sessionId: string
  target: string
  mode: string
  model: string
  status: string
  risk: string
  messages: Message[]
  plan: PlanStep[]
  evidence: string[]
  resources: Record<string, unknown>
  reportPath: string
  rawExpanded: boolean
  approvalPending: boolean
}

export const initialState: AppState = {
  sessionId: '',
  target: 'localhost',
  mode: 'demo',
  model: 'default',
  status: 'idle',
  risk: 'unknown',
  messages: [{ role: 'assistant', content: '你好，我是 OpsPilot。描述故障，或输入 /help。' }],
  plan: [],
  evidence: [],
  resources: {},
  reportPath: '',
  rawExpanded: false,
  approvalPending: false,
}
