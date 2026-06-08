import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { MonitorPane } from '../src/components/MonitorPane.js'

test('monitor shows normalized and raw process cpu', () => {
  const view = render(<MonitorPane resources={{
    sampler_status: 'ready',
    system: { cpu_percent: 10, memory_percent: 40, memory_total_gb: 32, logical_cpu_count: 10 },
    disk: { percent: 20, mountpoint: 'D:', used_gb: 1, total_gb: 2 },
    top_cpu_processes: [{ pid: 99, name: 'msedge', raw_cpu_percent: 655, normalized_cpu_percent: 65.5, memory_bytes: 1024 }],
    top_memory_processes: [{ pid: 99, name: 'msedge', raw_cpu_percent: 655, normalized_cpu_percent: 65.5, memory_bytes: 1024 }],
  }} history={[]} />)
  expect(view.lastFrame()).toContain('655% raw')
  expect(view.lastFrame()).toContain('msedge')
})
