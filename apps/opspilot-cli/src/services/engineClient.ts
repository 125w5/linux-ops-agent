import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { createInterface } from 'node:readline'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

export type RpcMessage = Record<string, unknown>

type PendingRequest = {
  resolve: (value: RpcMessage) => void
  timer?: ReturnType<typeof setTimeout>
}

export class EngineClient {
  private child: ChildProcessWithoutNullStreams
  private nextId = 1
  private pending = new Map<number, PendingRequest>()
  private stderrLines: string[] = []
  readonly cwd: string
  readonly pid?: number
  onEvent?: (event: string, payload: Record<string, unknown>) => void
  onError?: (payload: Record<string, unknown>) => void
  onClose?: (payload: Record<string, unknown>) => void

  constructor(command = preferredPython(), args = ['-m', 'diag', 'engine', '--stdio'], cwd = projectRoot()) {
    this.cwd = cwd
    this.child = spawn(command, args, {
      cwd,
      stdio: 'pipe',
      env: { ...process.env, PYTHONPATH: cwd, PYTHONIOENCODING: 'utf-8' },
    })
    this.pid = this.child.pid
    const lines = createInterface({ input: this.child.stdout })
    lines.on('line', line => this.handleLine(line))
    const errLines = createInterface({ input: this.child.stderr })
    errLines.on('line', line => this.rememberStderr(line))
    this.child.on('error', error => {
      this.onError?.({ message: error.message, cwd: this.cwd, stderr: this.recentStderr(), pid: this.pid })
    })
    this.child.on('close', (code, signal) => {
      for (const [id, pending] of this.pending) {
        if (pending.timer) {
          clearTimeout(pending.timer)
        }
        pending.resolve({ id, error: { code: -32002, message: `engine closed code=${String(code)} signal=${String(signal)}`, stderr: this.recentStderr(), cwd: this.cwd } })
      }
      this.pending.clear()
      this.onClose?.({ code: code ?? null, signal: signal ?? null, stderr: this.recentStderr(), cwd: this.cwd, pid: this.pid })
    })
  }

  request(method: string, params: Record<string, unknown> = {}, timeoutMs = 0): Promise<RpcMessage> {
    const id = this.nextId++
    const payload = { jsonrpc: '2.0', id, method, params }
    return new Promise(resolveRequest => {
      const pending: PendingRequest = { resolve: resolveRequest }
      if (timeoutMs > 0) {
        pending.timer = setTimeout(() => {
          this.pending.delete(id)
          resolveRequest({
            id,
            error: {
              code: -32001,
              message: `${method} timed out after ${timeoutMs}ms`,
              stderr: this.recentStderr(),
              cwd: this.cwd,
              pid: this.pid,
            },
          })
        }, timeoutMs)
      }
      this.pending.set(id, pending)
      try {
        this.child.stdin.write(`${JSON.stringify(payload)}\n`, 'utf8')
      } catch (error) {
        if (pending.timer) {
          clearTimeout(pending.timer)
        }
        this.pending.delete(id)
        resolveRequest({ id, error: { code: -32003, message: error instanceof Error ? error.message : String(error), stderr: this.recentStderr(), cwd: this.cwd, pid: this.pid } })
      }
    })
  }

  recentStderr(): string[] {
    return [...this.stderrLines]
  }

  close(): void {
    this.child.kill()
  }

  private rememberStderr(line: string): void {
    this.stderrLines = [...this.stderrLines, line].slice(-50)
  }

  private handleLine(line: string): void {
    let message: RpcMessage
    try {
      message = JSON.parse(line) as RpcMessage
    } catch (error) {
      this.rememberStderr(`invalid json from engine: ${line.slice(0, 300)}`)
      this.onError?.({ message: error instanceof Error ? error.message : String(error), line, stderr: this.recentStderr(), cwd: this.cwd, pid: this.pid })
      return
    }
    if (message.event && this.onEvent) {
      this.onEvent(String(message.event), message.payload as Record<string, unknown> ?? {})
      return
    }
    const id = Number(message.id)
    const pending = this.pending.get(id)
    if (pending) {
      if (pending.timer) {
        clearTimeout(pending.timer)
      }
      this.pending.delete(id)
      pending.resolve(message)
    }
  }
}

export function projectRoot(): string {
  return resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..')
}

export function preferredPython(): string {
  return process.env.OPSPILOT_PYTHON || process.env.PYTHON || 'python'
}
