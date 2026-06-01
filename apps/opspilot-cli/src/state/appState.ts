import type { ActionCard, Message, PlanStep } from './events.js'

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
  actions: ActionCard[]
  resources: Record<string, unknown>
  resourceHistory: Record<string, unknown>[]
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
  messages: [{ role: 'assistant', content: greetingText() }],
  plan: [],
  evidence: [],
  actions: [],
  resources: {},
  resourceHistory: [],
  reportPath: '',
  rawExpanded: false,
  approvalPending: false,
}

function greetingText(): string {
  return `${String.fromCodePoint(0x4f60, 0x597d, 0xff0c, 0x6211, 0x662f)} OpsPilot${String.fromCodePoint(0x3002, 0x63cf, 0x8ff0, 0x6545, 0x969c, 0xff0c, 0x6216, 0x8f93, 0x5165)} /help${String.fromCodePoint(0x3002)}`
}
