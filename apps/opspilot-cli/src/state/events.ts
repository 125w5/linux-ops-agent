export type EngineEvent = {
  event: string
  payload: Record<string, unknown>
}

export type Message = {
  role: 'user' | 'assistant' | 'tool' | 'system'
  content: string
  actions?: ActionCard[]
}

export type ActionCard = {
  label: string
  command: string
  source?: string
  risk?: string
  shortcut?: string
}

export type PlanStep = {
  id: string
  name: string
  command: string
  risk: string
  status?: string
}
