import React from 'react'
import { expect, test } from 'bun:test'
import { render } from 'ink-testing-library'
import { MonitorPane } from '../src/components/MonitorPane.js'
import { initialState } from '../src/state/appState.js'
import { reducer } from '../src/state/reducer.js'

test('telemetry stalled state is visible', () => {
  const view = render(<MonitorPane compact resources={{ telemetry_stalled: true }} history={[]} />)
  expect(view.lastFrame()).toContain('Telemetry stalled')
})

test('telemetry status event stores resource status', () => {
  const state = reducer(initialState, { type: 'engine-event', event: { event: 'TelemetryStatus', payload: { sampler_status: 'starting' } } })
  expect(state.resources.sampler_status).toBe('starting')
})
