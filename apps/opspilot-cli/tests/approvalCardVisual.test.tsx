import { expect, test } from 'bun:test'
import { ApprovalCard } from '../src/components/ApprovalCard.js'

test('approval card shows approval buttons and blocked card disables approval', () => {
  const approval = JSON.stringify(ApprovalCard({ action: 'process.kill_term', target: 'PID 42', command: 'kill -TERM 42', risk: 'low_risk', sandboxProfile: 'admin-confirm', reason: 'requires confirmation' }))
  const blocked = JSON.stringify(ApprovalCard({ action: 'process.kill_kill', target: 'PID 42', command: 'kill -9 42', risk: 'blocked', sandboxProfile: 'admin-confirm', reason: 'blocked' }))

  expect(approval).toContain('/approve')
  expect(approval).toContain('/deny')
  expect(blocked).toContain('Approval is not available')
})
