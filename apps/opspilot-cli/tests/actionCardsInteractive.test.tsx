import { expect, test } from 'bun:test'
import { actionByIndex, defaultActions } from '../src/actions/registry.js'
import { ActionBar } from '../src/components/ActionBar.js'

test('action cards render selectable numeric commands', () => {
  const tree = ActionBar({ actions: defaultActions, selectedIndex: 0 })

  expect(actionByIndex(defaultActions, 1)?.command).toBe('/run')
  expect(JSON.stringify(tree)).toContain('Run diagnosis')
  expect(JSON.stringify(tree)).toContain('/run')
})
