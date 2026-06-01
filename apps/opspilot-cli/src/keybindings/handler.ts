import { defaultKeybindings } from './defaults.js'

export function describeKeybindings(): string {
  return Object.entries(defaultKeybindings).map(([name, keys]) => `${name}: ${keys.join(', ')}`).join('\n')
}
