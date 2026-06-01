export type SlashCommand = {
  name: string
  description: string
}

export const slashCommands: SlashCommand[] = [
  { name: '/help', description: 'Show commands' },
  { name: '/run', description: 'Run current plan' },
  { name: '/raw', description: 'Toggle raw output' },
  { name: '/report', description: 'Show report path' },
  { name: '/resources', description: 'Show resource snapshot' },
  { name: '/model', description: 'Model configuration' },
  { name: '/config', description: 'Provider/API configuration' },
  { name: '/plugin', description: 'Plugin management' },
  { name: '/approve', description: 'Approve pending action' },
  { name: '/deny', description: 'Deny pending action' },
  { name: '/exit', description: 'Exit OpsPilot' },
]
