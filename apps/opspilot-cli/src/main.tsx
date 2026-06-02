#!/usr/bin/env bun
import { Command } from 'commander'
import { startApp } from './app.js'

const program = new Command()

program
  .name('opspilot')
  .description('OpsPilot conversational terminal agent')
  .option('--target <target>', 'target host', 'localhost')
  .option('--mode <mode>', 'permission mode', 'readonly')
  .action(options => startApp({ target: options.target, mode: options.mode }))

program.parse()
