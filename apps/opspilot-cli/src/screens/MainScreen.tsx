import React, { useCallback, useEffect, useMemo, useReducer, useRef, useState } from 'react'
import { useApp, useInput } from 'ink'
import type { AppState } from '../state/appState.js'
import { reducer } from '../state/reducer.js'
import { AppShell } from '../components/AppShell.js'
import { currentViewport } from '../layout/viewport.js'
import { actionByIndex, apiConfigActions, defaultActions, modelActions } from '../actions/registry.js'
import { EngineClient, type RpcMessage } from '../services/engineClient.js'
import type { ActionCard } from '../state/events.js'
import { searchMessages } from '../components/MessageSearch.js'
import { API_PROVIDER_CHOICES } from '../services/apiConfig.js'
import { useThrottledEvents } from '../hooks/useThrottledEvents.js'

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
  const [selectedActionIndex, setSelectedActionIndex] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')
  const stateRef = useRef(state)
  const clientRef = useRef<EngineClient | null>(null)
  const { exit } = useApp()
  const viewport = currentViewport()
  const dispatchEngineEvent = useCallback((event: { event: string; payload: Record<string, unknown> }) => {
    dispatch({ type: 'engine-event', event })
  }, [])
  const onEngineEvent = useThrottledEvents(dispatchEngineEvent)

  stateRef.current = state
  const client = useMemo(() => new EngineClient(), [])

  useEffect(() => {
    clientRef.current = client
    client.onEvent = (event, payload) => {
      if (['SessionStarted', 'EngineReady', 'EngineFailed', 'TelemetryStatus', 'TelemetryError', 'ResourceUpdated'].includes(event)) {
        dispatch({ type: 'engine-event', event: { event, payload } })
      } else {
        onEngineEvent(event, payload)
      }
    }
    client.onError = payload => dispatch({ type: 'engine-failed', payload })
    client.onClose = payload => dispatch({ type: 'engine-closed', payload })
    let mounted = true
    let resourceInFlight = false
    const requestResources = (sessionId?: string): void => {
      if (resourceInFlight) {
        return
      }
      resourceInFlight = true
      void client.request('resources.snapshot', { session_id: sessionId || stateRef.current.sessionId || undefined }, 5000).then(response => {
        resourceInFlight = false
        if (!mounted) return
        if (response.error) {
          dispatch({ type: 'engine-event', event: { event: 'TelemetryError', payload: { error: String((response.error as Record<string, unknown>).message ?? 'telemetry request failed'), stderr: client.recentStderr() } } })
        } else if (response.result) {
          dispatch({ type: 'engine-event', event: { event: 'ResourceUpdated', payload: response.result as Record<string, unknown> } })
        }
      })
    }
    void client.request('session.start', { target, mode, task: 'disk', client_pid: process.pid }, 2000).then(response => {
      if (!mounted) return
      if (response.error) {
        dispatch({ type: 'engine-failed', payload: { ...(response.error as Record<string, unknown>), pid: client.pid, cwd: client.cwd, stderr: client.recentStderr() } })
      } else if (response.result) {
        dispatch({ type: 'engine-event', event: { event: 'SessionStarted', payload: response.result as Record<string, unknown> } })
        const sessionId = String((response.result as Record<string, unknown>).session_id ?? '')
        requestResources(sessionId)
      }
    })
    const firstTelemetry = setTimeout(() => {
      if (mounted && stateRef.current.engine.lastResourceAt === undefined) {
        dispatch({ type: 'engine-event', event: { event: 'TelemetryStatus', payload: { telemetry_stalled: true, sampler_status: 'stalled', engine_status: stateRef.current.engine.status } } })
      }
    }, 3000)
    const timer = setInterval(() => {
      requestResources()
    }, 1000)
    return () => {
      mounted = false
      clearTimeout(firstTelemetry)
      clearInterval(timer)
      client.close()
    }
  }, [client, mode, onEngineEvent, target])

  useEffect(() => {
    dispatch({ type: 'viewport-height', height: viewport.bodyHeight })
  }, [viewport.bodyHeight])

  useInput((chunk, key) => {
    if (key.upArrow) {
      if (stateRef.current.activePanel === 'Config' && stateRef.current.configFlow) {
        dispatch({ type: 'api-wizard-provider', delta: -1 })
      }
      return
    }
    if (key.downArrow) {
      if (stateRef.current.activePanel === 'Config' && stateRef.current.configFlow) {
        dispatch({ type: 'api-wizard-provider', delta: 1 })
      }
      return
    }
    if (key.leftArrow) {
      setSelectedActionIndex(index => Math.max(0, index - 1))
      return
    }
    if (key.rightArrow) {
      setSelectedActionIndex(index => Math.min(Math.max(stateRef.current.actions.length - 1, 0), index + 1))
      return
    }
    if (key.pageUp) {
      dispatch({ type: 'scroll', delta: -Math.max(1, stateRef.current.scroll.viewportHeight - 2) })
      return
    }
    if (key.pageDown) {
      dispatch({ type: 'scroll', delta: Math.max(1, stateRef.current.scroll.viewportHeight - 2) })
      return
    }
    if (key.ctrl && chunk.toLowerCase() === 'j') {
      dispatch({ type: 'scroll-latest' })
      return
    }
    if (key.tab) {
      dispatch({ type: 'side-panel-next' })
      return
    }
    const functionPanel = panelFromFunctionKey(chunk)
    if (functionPanel) {
      dispatch({ type: 'side-panel', panel: functionPanel })
      return
    }
    if (/^[1-9]$/.test(chunk) && input.length === 0) {
      void runActionIndex(Number(chunk))
      return
    }
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
  }, { isActive: Boolean(process.stdin.isTTY) })

  async function submit(text: string): Promise<void> {
    if (!text) {
      if (stateRef.current.activePanel === 'Config' && stateRef.current.configFlow && stateRef.current.apiWizard.step === 'provider') {
        await submit(`/config api ${selectedProviderValue()}`)
        dispatch({ type: 'api-wizard-step', step: 'base_url' })
        return
      }
      await runActionIndex(selectedActionIndex + 1)
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
    if (text === '/cancel') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      if (clientRef.current) {
        appendResultText(await clientRef.current.request('cancel', { session_id: stateRef.current.sessionId || undefined }), 'Cancelled.')
      } else {
        dispatch({ type: 'message', message: { role: 'assistant', content: '已取消当前后台响应；你可以继续输入。' } })
      }
      return
    }
    if (isGreeting(text)) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({
        type: 'message',
        message: {
          role: 'assistant',
          content: `${String.fromCodePoint(0x4f60, 0x597d, 0xff0c, 0x6211, 0x5728, 0x3002)}${String.fromCodePoint(0x4f60, 0x53ef, 0x4ee5, 0x76f4, 0x63a5, 0x8bf4)}"${String.fromCodePoint(0x54ea, 0x4e2a, 0x8fdb, 0x7a0b, 0x5360)} CPU"${String.fromCodePoint(0x3001, 0x8f93, 0x5165)} /run${String.fromCodePoint(0xff0c, 0x6216, 0x7528)} /config api ${String.fromCodePoint(0x914d, 0x7f6e, 0x8fdc, 0x7a0b)} API${String.fromCodePoint(0x3002)}`,
          actions: [
            { label: `${String.fromCodePoint(0x67e5, 0x770b, 0x8d44, 0x6e90)}`, command: '/resources' },
            { label: `${String.fromCodePoint(0x914d, 0x7f6e)} API`, command: '/config api' },
            { label: `${String.fromCodePoint(0x5e2e, 0x52a9)}`, command: '/help' },
          ],
        },
      })
      return
    }
    if (text === '/raw') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'raw-toggle' })
      return
    }
    if (text === '/approve') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      await approvePendingAction()
      return
    }
    if (text === '/deny') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      await denyPendingAction()
      return
    }
    if (text === '/help') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'message', message: { role: 'assistant', content: helpText() } })
      return
    }
    if (text.startsWith('/message search ')) {
      const keyword = text.slice('/message search '.length).trim()
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      setSearchTerm(keyword)
      const matches = searchMessages(stateRef.current.messages, keyword)
      dispatch({ type: 'message', message: { role: 'assistant', content: `Search ${keyword}: ${matches.length} matches`, actions: [{ label: 'Jump latest', command: '/jump latest' }, { label: 'Clear search', command: '/message search' }] } })
      return
    }
    if (text === '/message search') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      setSearchTerm('')
      dispatch({ type: 'message', message: { role: 'assistant', content: 'Search cleared.', actions: defaultActions } })
      return
    }
    if (text === '/jump latest') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      setSearchTerm('')
      dispatch({ type: 'scroll-latest' })
      dispatch({ type: 'message', message: { role: 'assistant', content: 'Jumped to latest message.' } })
      return
    }

    const activeClient = clientRef.current
    if (!activeClient) {
      return
    }
    const session_id = stateRef.current.sessionId || undefined
    if (text === '/run') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Task' })
      await requestAndReport(activeClient, 'plan.run', { session_id })
      appendResultText(await activeClient.request('run.summary', { session_id }), undefined, runSummaryActions())
      return
    }
    if (text === '/resources') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Resources' })
      await activeClient.request('resources.snapshot', { session_id })
      appendResultText(await activeClient.request('resources.analyze', { session_id, focus: 'overview' }))
      return
    }
    if (text === '/monitor doctor' || text === '/telemetry doctor') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Resources' })
      const response = await activeClient.request('telemetry.doctor', { session_id })
      const result = response.result as Record<string, unknown> | undefined
      dispatch({ type: 'engine-event', event: { event: 'TelemetryDoctor', payload: result ?? {} } })
      appendResultText(response)
      return
    }
    if (text === '/latency') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Raw' })
      const response = await activeClient.request('latency.trace', { session_id })
      const result = response.result as Record<string, unknown> | undefined
      dispatch({ type: 'engine-event', event: { event: 'LatencyTrace', payload: result ?? {} } })
      appendResultText(response)
      return
    }
    if (text === '/report') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Report' })
      appendResultText(await activeClient.request('report.generate', { session_id }))
      return
    }
    if (text === '/process' || text.startsWith('/process ')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Process' })
      await handleProcess(activeClient, text, session_id, appendResultText)
      return
    }
    if (isProcessQuestion(text)) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Process' })
      const method = isMemoryQuestion(text) ? 'process.list_top_memory' : 'process.list_top_cpu'
      appendResultText(await activeClient.request(method, { session_id }))
      return
    }
    if (text.startsWith('/model')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      await handleModel(activeClient, text)
      return
    }
    if (text.startsWith('/config api')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Config' })
      await handleConfigApi(activeClient, text)
      return
    }
    if (text.startsWith('/config')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'message', message: { role: 'assistant', content: configHelpText(), actions: apiConfigActions() } })
      return
    }
    if (text.startsWith('/permissions')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'side-panel', panel: 'Task' })
      await handlePermissions(activeClient, text)
      return
    }
    if (text === '/tools' || text.startsWith('/tools ')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      appendResultText(await activeClient.request('tools.list'), undefined, toolActions())
      return
    }
    if (text === '/agents' || text.startsWith('/agents ')) {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      appendResultText(await activeClient.request('agents.list', { session_id }), undefined, agentActions())
      return
    }
    if (text === '/compact') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      appendResultText(await activeClient.request('context.compact', { session_id }))
      return
    }
    if (text === '/doctor') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      appendResultText(await activeClient.request('doctor.full', { session_id }))
      return
    }
    if (text === '/usage' || text === '/cost') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      appendResultText(await activeClient.request('usage.summary', { session_id }))
      return
    }
    if (text === '/session' || text === '/resume') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      appendResultText(await activeClient.request('session.info', { session_id }))
      return
    }
    if (text === '/clear') {
      await activeClient.request('session.clear', { session_id })
      dispatch({ type: 'clear-messages' })
      dispatch({ type: 'message', message: { role: 'assistant', content: 'Conversation cleared. API config, model, and sandbox profile are preserved.' } })
      return
    }
    if (text === '/fast') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'message', message: { role: 'assistant', content: 'Fast mode: short plans and action cards first; detailed explanation only when you ask.', actions: defaultFastActions() } })
      return
    }
    if (text === '/rewind') {
      dispatch({ type: 'message', message: { role: 'user', content: text } })
      dispatch({ type: 'message', message: { role: 'assistant', content: 'Rewind is staged for the next snapshot-aware session store. Current plan/report state is unchanged.' } })
      return
    }
    dispatch({ type: 'message', message: { role: 'assistant', content: '收到，正在判断任务类型...' } })
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

  async function runActionIndex(index: number): Promise<void> {
    const selected = actionByIndex(stateRef.current.actions, index)
    if (selected) {
      await submit(selected.command)
    }
  }

  function selectedProviderValue(): string {
    return API_PROVIDER_CHOICES[stateRef.current.apiWizard.selectedProviderIndex]?.value ?? 'deepseek'
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

  async function handlePermissions(activeClient: EngineClient, text: string): Promise<void> {
    const parts = text.split(/\s+/)
    const session_id = stateRef.current.sessionId || undefined
    if (parts[1] && parts[1] !== 'list') {
      appendResultText(await activeClient.request('permissions.set', { session_id, profile: parts[1] }), undefined, permissionsActions())
      return
    }
    appendResultText(await activeClient.request('permissions.list', { session_id }), undefined, permissionsActions())
  }

  async function approvePendingAction(): Promise<void> {
    const activeClient = clientRef.current
    const request = stateRef.current.approvalRequest
    if (!activeClient || !request) {
      dispatch({ type: 'message', message: { role: 'assistant', content: 'No approval is pending.' } })
      return
    }
    if (request.risk === 'blocked') {
      dispatch({ type: 'message', message: { role: 'assistant', content: 'This operation is blocked and cannot be approved.' } })
      return
    }
    const termMatch = request.command.match(/^kill\s+-TERM\s+(\d+)$/i)
    if (termMatch) {
      appendResultText(await activeClient.request('process.kill_term', { session_id: stateRef.current.sessionId || undefined, pid: termMatch[1], approved: true }))
      return
    }
    appendResultText(await activeClient.request('approval.resolve', { session_id: stateRef.current.sessionId || undefined, approved: true }))
  }

  async function denyPendingAction(): Promise<void> {
    const activeClient = clientRef.current
    if (!activeClient) {
      return
    }
    appendResultText(await activeClient.request('approval.resolve', { session_id: stateRef.current.sessionId || undefined, approved: false }), 'Denied.')
  }

  function dispatchConfigFlow(response: RpcMessage, prefix: string): void {
    if (response.error) {
      appendResultText(response)
      return
    }
    const result = response.result as Record<string, unknown> | undefined
    const flow = result?.flow as Record<string, unknown> | undefined
    dispatch({
      type: 'config-flow',
      flow: flow ? {
        provider: String(flow.provider ?? 'deepseek'),
        type: flow.type ? String(flow.type) : undefined,
        baseUrl: flow.base_url ? String(flow.base_url) : undefined,
        model: String(flow.model ?? ''),
        apiKeyEnv: flow.api_key_env ? String(flow.api_key_env) : undefined,
      } : null,
    })
    dispatch({ type: 'side-panel', panel: 'Config' })
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

  function appendResultText(response: RpcMessage, fallback?: string, actions?: ActionCard[]): void {
    if (response.error) {
      const error = response.error as Record<string, unknown>
      dispatch({ type: 'message', message: { role: 'assistant', content: `Request failed: ${String(error.message ?? 'unknown error')}` } })
      return
    }
    const result = response.result as Record<string, unknown> | undefined
    const text = result?.text ?? result?.message ?? result?.yaml ?? formatStructuredResult(result) ?? fallback
    const resultActions = Array.isArray(result?.actions) ? result.actions as ActionCard[] : undefined
    const messageActions = actions ?? resultActions
    if (text) {
      dispatch({ type: 'message', message: { role: 'assistant', content: String(text), actions: messageActions } })
      if (messageActions?.length) {
        setSelectedActionIndex(0)
      }
    }
  }

  function closeAndExit(): void {
    clientRef.current?.close()
    exit()
  }

  return <AppShell state={state} input={input} selectedActionIndex={selectedActionIndex} searchTerm={searchTerm} viewport={viewport} />
}

function isGreeting(text: string): boolean {
  const value = text.trim().toLowerCase()
  const nihao = String.fromCodePoint(0x4f60, 0x597d)
  const ninhao = String.fromCodePoint(0x60a8, 0x597d)
  return [nihao, ninhao, 'hi', 'hello', 'hey'].includes(value)
}

function isProcessQuestion(text: string): boolean {
  const value = text.trim().toLowerCase()
  const keywords = [
    `${String.fromCodePoint(0x54ea, 0x4e2a, 0x8fdb, 0x7a0b, 0x5360)} cpu`,
    `${String.fromCodePoint(0x9ad8)} cpu ${String.fromCodePoint(0x8fdb, 0x7a0b)}`,
    String.fromCodePoint(0x54ea, 0x4e9b, 0x8fdb, 0x7a0b, 0x5360, 0x5185, 0x5b58),
    String.fromCodePoint(0x5360, 0x5185, 0x5b58),
    '? cpu',
    `kill ${String.fromCodePoint(0x8fdb, 0x7a0b)}`,
    String.fromCodePoint(0x6740, 0x6389, 0x8fdb, 0x7a0b),
    String.fromCodePoint(0x67e5, 0x770b, 0x8fdb, 0x7a0b, 0x6811),
    'top cpu',
    'top memory',
    'process',
  ]
  return keywords.some(keyword => value.includes(keyword))
}

function isMemoryQuestion(text: string): boolean {
  const value = text.trim().toLowerCase()
  return value.includes(String.fromCodePoint(0x5185, 0x5b58)) || value.includes('memory') || value.includes('mem')
}

function panelFromFunctionKey(chunk: string): AppState['activePanel'] | null {
  if (chunk === '\u001bOQ') return 'Raw'
  if (chunk === '\u001bOR') return 'Resources'
  if (chunk === '\u001bOS') return 'Report'
  if (chunk === '\u001b[17~') return 'Evidence'
  if (chunk === '\u001b[18~') return 'Process'
  if (chunk === '\u001b[19~') return 'Config'
  return null
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
    { label: 'Use DeepSeek V4', command: '/config api model deepseekv4' },
    { label: 'Run diagnosis', command: '/run' },
  ]
}

async function handleProcess(
  activeClient: EngineClient,
  text: string,
  session_id: string | undefined,
  appendResultText: (response: RpcMessage, fallback?: string, actions?: ActionCard[]) => void,
): Promise<void> {
  const parts = text.split(/\s+/)
  if (parts[1] === 'inspect' && parts[2]) {
    appendResultText(await activeClient.request('process.inspect', { session_id, pid: parts[2] }))
    return
  }
  if (parts[1] === 'tree' && parts[2]) {
    appendResultText(await activeClient.request('process.tree', { session_id, pid: parts[2] }))
    return
  }
  if (parts[1] === 'term' && parts[2]) {
    appendResultText(await activeClient.request('process.kill_term', { session_id, pid: parts[2] }))
    return
  }
  if (parts[1] === 'kill' && parts[2]) {
    appendResultText(await activeClient.request('process.kill_kill', { session_id, pid: parts[2] }))
    return
  }
  appendResultText(await activeClient.request('process.list_top_cpu', { session_id }))
}

function helpText(): string {
  return [
    'Commands:',
    '/run run current plan',
    '/raw toggle raw output',
    '/resources refresh resource snapshot',
    '/process show process action cards',
    '/process inspect <pid> | tree <pid> | term <pid> | kill <pid>',
    '/model list | /model doctor [provider] | /model use provider:model',
    '/config api [provider] start API setup',
    '/config api model <name> | env <ENV> | base-url <url> | save',
    '/permissions [safe-read|ops-read|lab-write|admin-confirm]',
    '/tools list registered tools',
    '/agents list subagent scopes',
    '/doctor check API, sandbox, plugins, tools',
    '/compact compact long context',
    '/usage | /cost show session counters',
    '/session | /resume show session state',
    '/fast prefer short responses and action cards',
    '/clear clear conversation and preserve config',
    '/action 1 or 1 run an action card',
    '/approve | /deny resolve the pending approval card',
    '/exit exit',
  ].join('\n')
}

function configHelpText(): string {
  return [
    'API setup:',
    '1. Store real keys in environment variables only.',
    '2. Use /config api deepseek to start the DeepSeek V4 preset.',
    '3. Use /config api model deepseekv4 to select the DeepSeek V4 model.',
    '4. Use /model doctor deepseek to check missing env vars.',
    '5. configs/local.yaml stores api_key_env, never the real key.',
  ].join('\n')
}

function runSummaryActions(): ActionCard[] {
  return [
    { label: 'Show raw', command: '/raw' },
    { label: 'Generate report', command: '/report' },
    { label: 'Explain evidence', command: '/help' },
  ]
}

function processActions(result: Record<string, unknown> | undefined): ActionCard[] {
  const rows = [
    ...(Array.isArray(result?.top_cpu_processes) ? result?.top_cpu_processes : []),
    ...(Array.isArray(result?.top_memory_processes) ? result?.top_memory_processes : []),
  ].filter(item => item && typeof item === 'object') as Array<Record<string, unknown>>
  return rows.slice(0, 4).flatMap(row => {
    const pid = String(row.pid ?? '')
    if (!pid) {
      return []
    }
    return [
      { label: `Inspect ${pid}`, command: `/process inspect ${pid}` },
      { label: `Tree ${pid}`, command: `/process tree ${pid}` },
      { label: `SIGTERM ${pid}`, command: `/process term ${pid}` },
      { label: `SIGKILL ${pid}`, command: `/process kill ${pid}` },
    ]
  })
}

function permissionsActions(): ActionCard[] {
  return [
    { label: 'Safe read', command: '/permissions safe-read' },
    { label: 'Ops read', command: '/permissions ops-read' },
    { label: 'Lab write', command: '/permissions lab-write' },
    { label: 'Admin confirm', command: '/permissions admin-confirm' },
  ]
}

function toolActions(): ActionCard[] {
  return [
    { label: 'Permissions', command: '/permissions' },
    { label: 'Agents', command: '/agents' },
    { label: 'Doctor', command: '/doctor' },
  ]
}

function agentActions(): ActionCard[] {
  return [
    { label: 'Tools', command: '/tools' },
    { label: 'Ops read sandbox', command: '/permissions ops-read' },
    { label: 'Run diagnosis', command: '/run' },
  ]
}

function defaultFastActions(): ActionCard[] {
  return [
    { label: 'Tools', command: '/tools' },
    { label: 'Permissions', command: '/permissions' },
    { label: 'Doctor', command: '/doctor' },
    { label: 'Run diagnosis', command: '/run' },
  ]
}

function formatStructuredResult(result: Record<string, unknown> | undefined): string | undefined {
  if (!result) {
    return undefined
  }
  if (Array.isArray(result.profiles)) {
    const profiles = result.profiles
      .map(item => item && typeof item === 'object' ? item as Record<string, unknown> : {})
      .map(item => `${String(item.name ?? '')}: ${String(item.description ?? '')}`)
      .filter(Boolean)
      .join('\n')
    return [`Current sandbox: ${String(result.current ?? 'safe-read')}`, String(result.description ?? ''), profiles].filter(Boolean).join('\n')
  }
  if (Array.isArray(result.tools)) {
    return result.tools
      .slice(0, 14)
      .map(item => item && typeof item === 'object' ? item as Record<string, unknown> : {})
      .map(item => `${String(item.name ?? '')} [${String(item.risk ?? '')}] ${String(item.description ?? '')}`)
      .join('\n')
  }
  if (Array.isArray(result.agents)) {
    return result.agents
      .map(item => item && typeof item === 'object' ? item as Record<string, unknown> : {})
      .map(item => `[${String(item.name ?? '')}] sandbox=${String(item.sandbox_profile ?? '')} scenes=${Array.isArray(item.tool_scenes) ? item.tool_scenes.join(',') : ''}`)
      .join('\n')
  }
  if (typeof result.compacted === 'boolean') {
    return result.compacted ? String(result.summary ?? 'Context compacted.') : 'Context is already short; no compaction needed.'
  }
  return undefined
}
