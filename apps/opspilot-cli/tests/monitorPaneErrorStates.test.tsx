import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { MonitorPane } from '../src/components/MonitorPane.js'

test('monitor shows sampler error instead of silent n/a', () => {
  const view = render(<MonitorPane resources={{ sampler_status: 'error', sampler_error: 'psutil missing', system: {}, disk: {} }} history={[]} />)
  expect(view.lastFrame()).toContain('psutil missing')
})

test('monitor shows sampling while process cpu warms up', () => {
  const view = render(<MonitorPane resources={{ sampler_status: 'warming_up', system: { cpu_percent: 1 }, disk: {} }} history={[]} />)
  expect(view.lastFrame()).toContain('sampling')
})
