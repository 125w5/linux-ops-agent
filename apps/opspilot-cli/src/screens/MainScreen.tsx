import React, { useEffect, useMemo, useReducer, useRef, useState } from 'react'
import { useApp, useInput } from 'ink'
import type { AppState } from '../state/appState.js'
import { reducer } from '../state/reducer.js'
import { AppShell } from '../components/AppShell.js'
import { EngineClient, type RpcMessage } from '../services/engineClient.js'

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
    if (chunk === '\u000d') {
      const submitted = input.trim()
      setInput('')
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
    if (text.startsWith('/config')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'message', message: { role: 'assistant', content: configHelpText() } })
      return
    }
    await requestAndReport(activeClient, 'chat.message', { session_id, text }, false)
  }

  async function handleModel(activeClient: EngineClient, text: string): Promise<void> {
    const parts = text.split(/\s+/)
    if (parts[1] === 'doctor') {
      const response = await activeClient.request('model.doctor', { provider: parts[2] })
      appendResultText(response)
      return
    }
    if (parts[1] === 'use' && parts[2]) {
      const response = await activeClient.request('model.set', { model: parts[2] })
      appendResultText(response, `已切换默认模型：${parts[2]}`)
      return
    }
    const response = await activeClient.request('model.list')
    appendResultText(response)
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

  function appendResultText(response: RpcMessage, fallback?: string): void {
    if (response.error) {
      const error = response.error as Record<string, unknown>
      dispatch({ type: 'message', message: { role: 'assistant', content: `请求失败：${String(error.message ?? 'unknown error')}` } })
      return
    }
    const result = response.result as Record<string, unknown> | undefined
    const text = result?.text ?? result?.message ?? fallback
    if (text) {
      dispatch({ type: 'message', message: { role: 'assistant', content: String(text) } })
    }
  }

  function closeAndExit(): void {
    clientRef.current?.close()
    exit()
  }

  return <AppShell state={state} input={input} />
}

function helpText(): string {
  return [
    '可用命令：',
    '/run 执行当前计划',
    '/raw 展开或折叠原始输出',
    '/resources 刷新资源快照',
    '/model list | /model doctor [provider] | /model use provider:model',
    '/config api 查看 API 配置方式',
    '/exit 退出',
  ].join('\n')
}

function configHelpText(): string {
  return [
    'API 配置方式：',
    '1. 真实密钥只放环境变量，例如 OPENAI_API_KEY。',
    '2. 用 /model doctor openai 检查环境变量。',
    '3. 用 /model use openai:gpt-4.1-mini 切换默认模型。',
    '4. 配置写入 configs/local.yaml，但不会保存真实 API key。',
  ].join('\n')
}
