import { slashCommands } from './slashCommands.js'

export function findCommands(prefix = '/'): typeof slashCommands {
  return slashCommands.filter(command => command.name.startsWith(prefix))
}

export function commandHelp(prefix = '/'): string {
  return findCommands(prefix).map(command => `${command.name.padEnd(12)} ${command.description}`).join('\n')
}
