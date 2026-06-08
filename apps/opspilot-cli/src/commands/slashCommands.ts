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
  { name: '/process', description: 'Inspect or terminate processes through approval UI' },
  { name: '/model', description: 'Model configuration' },
  { name: '/config', description: 'Provider/API configuration' },
  { name: '/plugin', description: 'Plugin management' },
  { name: '/permissions', description: 'Sandbox profiles' },
  { name: '/fast', description: 'Fast response mode' },
  { name: '/message', description: 'Search conversation messages' },
  { name: '/jump', description: 'Jump within the message stream' },
  { name: '/compact', description: 'Compact conversation context' },
  { name: '/agents', description: 'Subagent scopes' },
  { name: '/tools', description: 'Tool registry' },
  { name: '/doctor', description: 'API, sandbox and tool doctor' },
  { name: '/cost', description: 'Session API/cost estimate' },
  { name: '/usage', description: 'Session usage counters' },
  { name: '/session', description: 'Session details' },
  { name: '/resume', description: 'Show current session state' },
  { name: '/clear', description: 'Clear conversation' },
  { name: '/rewind', description: 'Rewind to previous plan/report state' },
  { name: '/approve', description: 'Approve pending action' },
  { name: '/deny', description: 'Deny pending action' },
  { name: '/exit', description: 'Exit OpsPilot' },
]
