import type { ActionCard } from '../state/events.js'

export const defaultActions: ActionCard[] = [
  { label: 'Run diagnosis', command: '/run' },
  { label: 'Configure API', command: '/config api' },
  { label: 'Show raw', command: '/raw' },
  { label: 'Change model', command: '/model doctor' },
]

export function actionByIndex(actions: ActionCard[], index: number): ActionCard | undefined {
  return actions[index - 1]
}
