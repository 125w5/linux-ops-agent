import type { ActionCard } from '../state/events.js'
import { API_PROVIDER_CHOICES } from '../services/apiConfig.js'

export const defaultActions: ActionCard[] = [
  { label: 'Run diagnosis', command: '/run', source: 'assistant', risk: 'safe-read', shortcut: '1' },
  { label: 'Configure API', command: '/config api', source: 'assistant', risk: 'safe-read', shortcut: '2' },
  { label: 'Show raw', command: '/raw', source: 'assistant', risk: 'safe-read', shortcut: '3' },
  { label: 'Change model', command: '/model doctor', source: 'assistant', risk: 'safe-read', shortcut: '4' },
]

export function actionByIndex(actions: ActionCard[], index: number): ActionCard | undefined {
  return actions[index - 1]
}

export function apiConfigActions(): ActionCard[] {
  return API_PROVIDER_CHOICES.map((choice, index) => ({
    label: choice.label,
    command: `/config api ${choice.value}`,
    source: 'api-wizard',
    risk: 'safe-read',
    shortcut: String(index + 1),
  }))
}

export function modelActions(): ActionCard[] {
  return [
    { label: 'List models', command: '/model list', source: 'model', risk: 'safe-read', shortcut: '1' },
    { label: 'Model doctor', command: '/model doctor', source: 'model', risk: 'safe-read', shortcut: '2' },
    { label: 'Configure API', command: '/config api', source: 'model', risk: 'safe-read', shortcut: '3' },
  ]
}
