import { expect, test } from 'bun:test'
import { commandHelp, findCommands } from '../src/commands/registry.js'

test('fast mode and low latency commands are in command palette', () => {
  const names = findCommands('/').map(command => command.name)

  expect(names).toContain('/fast')
  expect(names).toContain('/compact')
  expect(commandHelp('/fast')).toContain('Fast response')
})
