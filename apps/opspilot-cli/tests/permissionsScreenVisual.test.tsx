import { expect, test } from 'bun:test'
import { PermissionsScreen } from '../src/screens/PermissionsScreen.js'

test('permissions screen shows profile cards', () => {
  const raw = JSON.stringify(PermissionsScreen({ current: 'ops-read' }))

  expect(raw).toContain('safe-read')
  expect(raw).toContain('ops-read')
  expect(raw).toContain('admin-confirm')
  expect(raw).toContain('dangerous')
})
