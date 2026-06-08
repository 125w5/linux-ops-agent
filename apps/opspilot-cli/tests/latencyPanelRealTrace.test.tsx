import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { LatencyPanel } from '../src/components/LatencyPanel.js'

test('latency panel renders real trace fields', () => {
  const view = render(<LatencyPanel trace={{ fast_router_ms: 2, api_call_count: 0, total_turn_ms: 5 }} />)
  expect(view.lastFrame()).toContain('fast_router_ms: 2')
  expect(view.lastFrame()).toContain('api_call_count: 0')
})
