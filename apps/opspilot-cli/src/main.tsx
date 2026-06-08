#!/usr/bin/env bun
import { Command } from 'commander'
import { startApp } from './app.js'
import { EngineClient } from './services/engineClient.js'

const program = new Command()

program
  .name('opspilot')
  .description('OpsPilot conversational terminal agent')
  .option('--target <target>', 'target host', 'localhost')
  .option('--mode <mode>', 'permission mode', 'readonly')
  .option('--smoke', 'run engine handshake smoke test')
  .action(async options => {
    if (options.smoke) {
      const client = new EngineClient()
      try {
        const session = await client.request('session.start', { target: options.target, mode: options.mode, task: 'disk' }, 2000)
        if (session.error || !(session.result as Record<string, unknown> | undefined)?.session_id) {
          console.error(`opspilot smoke failed: ${JSON.stringify(session.error ?? session.result)}`)
          process.exitCode = 1
          return
        }
        const sessionId = String((session.result as Record<string, unknown>).session_id)
        const resources = await client.request('resources.snapshot', { session_id: sessionId }, 6000)
        if (resources.error) {
          console.error(`opspilot smoke failed: ${JSON.stringify(resources.error)}`)
          process.exitCode = 1
          return
        }
        const doctor = await client.request('telemetry.doctor', { session_id: sessionId }, 3000)
        if (doctor.error) {
          console.error(`opspilot smoke failed: ${JSON.stringify(doctor.error)}`)
          process.exitCode = 1
          return
        }
        console.log(`opspilot smoke ok session=${sessionId}`)
      } finally {
        client.close()
      }
      return
    }
    startApp({ target: options.target, mode: options.mode })
  })

program.parse()
