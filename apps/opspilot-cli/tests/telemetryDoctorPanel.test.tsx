import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { TelemetryDoctorPanel } from '../src/components/TelemetryDoctorPanel.js'

test('telemetry doctor renders schema and psutil status', () => {
  const view = render(<TelemetryDoctorPanel doctor={{ platform: 'win', python_version: '3.13', psutil_available: false, logical_cpu_count: 12, sampler_status: 'error', sampler_error: 'psutil missing', schema: { ok: false, errors: ['missing memory'] } }} />)
  expect(view.lastFrame()).toContain('psutil missing')
  expect(view.lastFrame()).toContain('missing memory')
})
