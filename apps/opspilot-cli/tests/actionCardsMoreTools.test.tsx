import { expect, test } from 'bun:test'
import { slashCommands } from '../src/commands/slashCommands.js'

test('expanded tool and agent commands are visible as slash commands', () => {
  const names = slashCommands.map(command => command.name)

  expect(names).toContain('/tools')
  expect(names).toContain('/agents')
  expect(names).toContain('/doctor')
})
