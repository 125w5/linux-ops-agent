#!/usr/bin/env bun
import { EngineClient } from './services/engineClient.js'

async function main(): Promise<number> {
  const client = new EngineClient()
  try {
    const session = await client.request('session.start', { target: 'localhost', mode: 'readonly', task: 'disk' }, 2000)
    if (session.error || !readObject(session.result).session_id) {
      console.error('session.start failed', JSON.stringify(session.error ?? session.result))
      return 1
    }
    const sessionId = String(readObject(session.result).session_id)
    const resource = await client.request('resources.snapshot', { session_id: sessionId }, 6000)
    if (resource.error) {
      console.error('resources.snapshot failed', JSON.stringify(resource.error))
      return 1
    }
    const result = readObject(resource.result)
    if (result.event !== 'ResourceUpdated' && result.sampler_status !== 'error') {
      console.error('no ResourceUpdated/TelemetryError', JSON.stringify(result))
      return 1
    }
    const doctor = await client.request('telemetry.doctor', { session_id: sessionId }, 2000)
    if (doctor.error) {
      console.error('telemetry.doctor failed', JSON.stringify(doctor.error))
      return 1
    }
    console.log(`opspilot smoke ok session=${sessionId} sampler=${String(result.sampler_status ?? 'unknown')}`)
    return 0
  } finally {
    client.close()
  }
}

function readObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {}
}

process.exitCode = await main()
