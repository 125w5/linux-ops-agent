import { expect, test } from 'bun:test'
import { commandHelp, findCommands } from '../src/commands/registry.js'

test('finds command palette entries by prefix', () => {
  const names = findCommands('/r').map(command => command.name)

  expect(names).toContain('/run')
  expect(names).toContain('/raw')
  expect(names).toContain('/report')
  expect(commandHelp('/config')).toContain('Provider/API')
})
