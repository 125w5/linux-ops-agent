import type { ActionCard } from '../state/events.js'
import { API_PROVIDER_CHOICES } from '../services/apiConfig.js'

export const defaultActions: ActionCard[] = [
  { label: 'Run diagnosis', command: '/run' },
  { label: 'Configure API', command: '/config api' },
  { label: 'Show raw', command: '/raw' },
  { label: 'Change model', command: '/model doctor' },
]

export function actionByIndex(actions: ActionCard[], index: number): ActionCard | undefined {
  return actions[index - 1]
}

export function apiConfigActions(): ActionCard[] {
  return API_PROVIDER_CHOICES.map(choice => ({
    label: choice.label,
    command: `/config api ${choice.value}`,
  }))
}

export function modelActions(): ActionCard[] {
  return [
    { label: 'List models', command: '/model list' },
    { label: 'Model doctor', command: '/model doctor' },
    { label: 'Configure API', command: '/config api' },
  ]
}
