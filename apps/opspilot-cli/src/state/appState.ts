import type { ActionCard, Message, PlanStep } from './events.js'
import { initialScrollState, type ScrollState } from './scrollState.js'

export type SidePanelName = 'Task' | 'Evidence' | 'Resources' | 'Raw' | 'Report' | 'Config' | 'Process' | 'Approval'

export type AppState = {
  sessionId: string
  target: string
  mode: string
  model: string
  status: string
  risk: string
  sandboxProfile: string
  latencyMs: number
  apiCalls: number
  estimatedTokens: number
  commandsExecuted: number
  outputBytes: number
  apiLatencyMs: number
  fallbackReason: string
  responding: boolean
  engine: {
    status: 'pending' | 'connected' | 'failed' | 'closed'
    pid?: number
    cwd?: string
    python?: string
    stderr: string[]
    error?: string
    startedAt: number
    lastResourceAt?: number
  }
  telemetryDoctor: Record<string, unknown> | null
  latencyTrace: Record<string, unknown>
  resourceSchemaError: string
  approvalRequest: {
    action: string
    command: string
    risk: string
    sandboxProfile: string
    reason: string
    target: string
  } | null
  configFlow: {
    provider: string
    type?: string
    baseUrl?: string
    model: string
    apiKeyEnv?: string
  } | null
  messages: Message[]
  plan: PlanStep[]
  evidence: string[]
  actions: ActionCard[]
  resources: Record<string, unknown>
  resourceHistory: Record<string, unknown>[]
  reportPath: string
  rawExpanded: boolean
  approvalPending: boolean
  scroll: ScrollState
  activePanel: SidePanelName
  sidePanelVisible: boolean
  apiWizard: {
    step: 'provider' | 'base_url' | 'model' | 'api_key_env' | 'preview'
    selectedProviderIndex: number
    error?: string
  }
}

export const initialState: AppState = {
  sessionId: '',
  target: 'localhost',
  mode: 'readonly',
  model: 'default',
  status: 'idle',
  risk: 'unknown',
  sandboxProfile: 'safe-read',
  latencyMs: 0,
  apiCalls: 0,
  estimatedTokens: 0,
  commandsExecuted: 0,
  outputBytes: 0,
  apiLatencyMs: 0,
  fallbackReason: '',
  responding: false,
  engine: {
    status: 'pending',
    stderr: [],
    startedAt: Date.now(),
  },
  telemetryDoctor: null,
  latencyTrace: {},
  resourceSchemaError: '',
  approvalRequest: null,
  configFlow: null,
  messages: [{ role: 'assistant', content: greetingText() }],
  plan: [],
  evidence: [],
  actions: [],
  resources: {},
  resourceHistory: [],
  reportPath: '',
  rawExpanded: false,
  approvalPending: false,
  scroll: initialScrollState,
  activePanel: 'Task',
  sidePanelVisible: true,
  apiWizard: {
    step: 'provider',
    selectedProviderIndex: 0,
  },
}

function greetingText(): string {
  return `${String.fromCodePoint(0x4f60, 0x597d, 0xff0c, 0x6211, 0x662f)} OpsPilot${String.fromCodePoint(0x3002, 0x63cf, 0x8ff0, 0x6545, 0x969c, 0xff0c, 0x6216, 0x8f93, 0x5165)} /help${String.fromCodePoint(0x3002)}`
}
