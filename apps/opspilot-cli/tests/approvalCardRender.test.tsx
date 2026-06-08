import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { ApprovalCard } from '../src/components/ApprovalCard.js'

test('ApprovalCard renders approval controls without naked Ink strings', () => {
  const view = render(<ApprovalCard action="process.kill_term" target="PID 42" command="kill -TERM 42" risk="low_risk" sandboxProfile="admin-confirm" reason="requires confirmation" />)

  expect(view.lastFrame()).toContain('/approve')
  view.unmount()
})
