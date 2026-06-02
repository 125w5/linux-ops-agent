import React, { useEffect, useMemo, useReducer, useRef, useState } from 'react'
import { useApp, useInput } from 'ink'
import type { AppState } from '../state/appState.js'
import { reducer } from '../state/reducer.js'
import { AppShell } from '../components/AppShell.js'
import { apiConfigActions, modelActions } from '../actions/registry.js'
import { EngineClient, type RpcMessage } from '../services/engineClient.js'
import type { ActionCard } from '../state/events.js'

export function MainScreen({
  initialState,
  target,
  mode,
}: {
  initialState: AppState
  target: string
  mode: string
}): React.ReactElement {
  const [state, dispatch] = useReducer(reducer, { ...initialState, target, mode })
  const [input, setInput] = useState('')
  const stateRef = useRef(state)
  const clientRef = useRef<EngineClient | null>(null)
  const { exit } = useApp()

  stateRef.current = state
  const client = useMemo(() => new EngineClient(), [])

  useEffect(() => {
    clientRef.current = client
    client.onEvent = (event, payload) => dispatch({ type: 'engine-event', event: { event, payload } })
    void client.request('session.start', { target, mode, task: 'disk' })
    const timer = setInterval(() => {
      void client.request('resources.snapshot')
    }, 1000)
    return () => {
      clearInterval(timer)
      client.close()
    }
  }, [client, mode, target])

  useInput((chunk, key) => {
    const newlineIndex = chunk.search(/[\r\n]/)
    if (key.return || newlineIndex >= 0) {
      const beforeNewline = newlineIndex >= 0 ? chunk.slice(0, newlineIndex) : ''
      const afterNewline = newlineIndex >= 0 ? chunk.slice(newlineIndex + 1).replace(/[\r\n]/g, '') : ''
      const submitted = `${input}${beforeNewline}`.trim()
      setInput(afterNewline)
      void submit(submitted)
      return
    }
    if (key.backspace || key.delete) {
      setInput(value => value.slice(0, -1))
      return
    }
    if (key.ctrl && chunk === 'c') {
      closeAndExit()
      return
    }
    if (chunk && !key.ctrl && !key.meta && chunk !== '\r' && chunk !== '\n') {
      setInput(value => value + chunk)
    }
  })

  async function submit(text: string): Promise<void> {
    if (!text) {
      return
    }
    const actionCommand = resolveAction(text)
    if (actionCommand) {
      await submit(actionCommand)
      return
    }
    if (text === '/exit') {
      closeAndExit()
      return
    }
    if (text === '/raw') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'raw-toggle' })
      return
    }
    if (text === '/help') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'message', message: { role: 'assistant', content: helpText() } })
      return
    }

    const activeClient = clientRef.current
    if (!activeClient) {
      return
    }
    const session_id = stateRef.current.sessionId || undefined
    if (text === '/run') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      await requestAndReport(activeClient, 'plan.run', { session_id })
      return
    }
    if (text === '/resources') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      await requestAndReport(activeClient, 'resources.snapshot', { session_id })
      return
    }
    if (text.startsWith('/model')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      await handleModel(activeClient, text)
      return
    }
    if (text.startsWith('/config api')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      await handleConfigApi(activeClient, text)
      return
    }
    if (text.startsWith('/config')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'message', message: { role: 'assistant', content: configHelpText(), actions: apiConfigActions() } })
      return
    }
    await requestAndReport(activeClient, 'chat.message', { session_id, text }, false)
  }

  function resolveAction(text: string): string | null {
    const trimmed = text.trim()
    const indexText = trimmed.startsWith('/action ') ? trimmed.slice('/action '.length) : trimmed
    if (!/^[1-9]\d*$/.test(indexText)) {
      return null
    }
    const action = stateRef.current.actions[Number(indexText) - 1]
    return action?.command ?? null
  }

  async function handleModel(activeClient: EngineClient, text: string): Promise<void> {
    const parts = text.split(/\s+/)
    if (!parts[1] || parts[1] === 'list') {
      appendResultText(await activeClient.request('model.list'), undefined, modelActions())
      return
    }
    if (parts[1] === 'doctor') {
      appendResultText(await activeClient.request('model.doctor', { provider: parts[2] }), undefined, modelActions())
      return
    }
    if (parts[1] === 'use' && parts[2]) {
      appendResultText(await activeClient.request('model.set', { model: parts[2] }), `Default model updated: ${parts[2]}`)
      return
    }
    appendResultText(await activeClient.request('model.list'))
  }

  async function handleConfigApi(activeClient: EngineClient, text: string): Promise<void> {
    const parts = text.split(/\s+/)
    const session_id = stateRef.current.sessionId || undefined
    if (parts[2] === 'preview') {
      appendResultText(await activeClient.request('config.api.preview', { session_id }))
      return
    }
    if (parts[2] === 'save') {
      appendResultText(await activeClient.request('config.api.save', { session_id }), undefined, [{ label: 'Model doctor', command: '/model doctor deepseek' }, { label: 'Run diagnosis', command: '/run' }])
      return
    }
    if (['base', 'base-url', 'base_url', 'url'].includes(parts[2] ?? '')) {
      const base_url = parts.slice(3).join(' ')
      const response = await activeClient.request('config.api.set_base_url', { session_id, base_url })
      dispatchConfigFlow(response, 'Base URL updated.')
      return
    }
    if (parts[2] === 'model') {
      const model = parts.slice(3).join(' ')
      const response = await activeClient.request('config.api.set_model', { session_id, model })
      dispatchConfigFlow(response, 'Model updated.')
      return
    }
    if (['env', 'key-env', 'api_key_env'].includes(parts[2] ?? '')) {
      const api_key_env = parts.slice(3).join(' ')
      const response = await activeClient.request('config.api.set_api_key_env', { session_id, api_key_env })
      dispatchConfigFlow(response, 'API key env updated.')
      return
    }
    const provider = parts[2]
    const response = await activeClient.request('config.api.start', provider ? { session_id, provider } : { session_id })
    dispatchConfigFlow(response, 'API setup started.')
  }

  function dispatchConfigFlow(response: RpcMessage, prefix: string): void {
    if (response.error) {
      appendResultText(response)
      return
    }
    const result = response.result as Record<string, unknown> | undefined
    const flow = result?.flow as Record<string, unknown> | undefined
    dispatch({
      type: 'message',
      message: {
        role: 'assistant',
        content: flow ? configFlowSummary(prefix, flow) : prefix,
        actions: configFlowActions(),
      },
    })
  }

  async function requestAndReport(
    activeClient: EngineClient,
    method: string,
    params: Record<string, unknown>,
    appendText = true,
  ): Promise<void> {
    const response = await activeClient.request(method, params)
    if (appendText || response.error) {
      appendResultText(response)
    }
  }

  function appendResultText(response: RpcMessage, fallback?: string, actions?: ReturnType<typeof modelActions>): void {
    if (response.error) {
      const error = response.error as Record<string, unknown>
      dispatch({ type: 'message', message: { role: 'assistant', content: `Request failed: ${String(error.message ?? 'unknown error')}` } })
      return
    }
    const result = response.result as Record<string, unknown> | undefined
    const text = result?.text ?? result?.message ?? result?.yaml ?? fallback
    if (text) {
      dispatch({ type: 'message', message: { role: 'assistant', content: String(text), actions } })
    }
  }

  function closeAndExit(): void {
    clientRef.current?.close()
    exit()
  }

  return <AppShell state={state} input={input} />
}

function configFlowSummary(prefix: string, flow: Record<string, unknown>): string {
  return [
    prefix,
    `provider=${String(flow.provider ?? 'deepseek')}`,
    `base_url=${String(flow.base_url ?? 'set later')}`,
    `model=${String(flow.model || 'set later')}`,
    `api_key_env=${String(flow.api_key_env || 'set later')}`,
    'Use /config api save to write configs/local.yaml. Put the real key in the environment variable only.',
  ].join('\n')
}

function configFlowActions(): ActionCard[] {
  return [
    { label: 'Save config', command: '/config api save' },
    { label: 'Preview config', command: '/config api preview' },
    { label: 'Model doctor', command: '/model doctor deepseek' },
    { label: 'Use V4 Pro', command: '/config api model deepseek-v4-pro' },
    { label: 'Run diagnosis', command: '/run' },
  ]
}

function helpText(): string {
  return [
    'Commands:',
    '/run run current plan',
    '/raw toggle raw output',
    '/resources refresh resource snapshot',
    '/model list | /model doctor [provider] | /model use provider:model',
    '/config api [provider] start API setup',
    '/config api model <name> | env <ENV> | base-url <url> | save',
    '/action 1 or 1 run an action card',
    '/exit exit',
  ].join('\n')
}

function configHelpText(): string {
  return [
    'API setup:',
    '1. Store real keys in environment variables only.',
    '2. Use /config api deepseek to start the DeepSeek V4 preset.',
    '3. Use /config api model deepseek-v4-pro to switch from flash to pro.',
    '4. Use /model doctor deepseek to check missing env vars.',
    '5. configs/local.yaml stores api_key_env, never the real key.',
  ].join('\n')
}
