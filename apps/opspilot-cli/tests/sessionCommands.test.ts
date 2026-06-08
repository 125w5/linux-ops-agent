import { expect, test } from 'bun:test'
import { slashCommands } from '../src/commands/slashCommands.js'

test('session lifecycle commands are registered', () => {
  const names = slashCommands.map(command => command.name)

  expect(names).toContain('/session')
  expect(names).toContain('/resume')
  expect(names).toContain('/clear')
  expect(names).toContain('/rewind')
})
