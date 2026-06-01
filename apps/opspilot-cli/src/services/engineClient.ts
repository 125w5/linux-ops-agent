import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { createInterface } from 'node:readline'

export type RpcMessage = Record<string, unknown>

export class EngineClient {
  private child: ChildProcessWithoutNullStreams
  private nextId = 1
  private pending = new Map<number, (value: RpcMessage) => void>()
  onEvent?: (event: string, payload: Record<string, unknown>) => void

  constructor(command = 'python', args = ['-m', 'diag', 'engine', '--stdio']) {
    this.child = spawn(command, args, { stdio: 'pipe', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } })
    const lines = createInterface({ input: this.child.stdout })
    lines.on('line', line => this.handleLine(line))
  }

  request(method: string, params: Record<string, unknown> = {}): Promise<RpcMessage> {
    const id = this.nextId++
    const payload = { jsonrpc: '2.0', id, method, params }
    this.child.stdin.write(`${JSON.stringify(payload)}\n`, 'utf8')
    return new Promise(resolve => this.pending.set(id, resolve))
  }

  close(): void {
    this.child.kill()
  }

  private handleLine(line: string): void {
    const message = JSON.parse(line) as RpcMessage
    if (message.event && this.onEvent) {
      this.onEvent(String(message.event), message.payload as Record<string, unknown> ?? {})
      return
    }
    const id = Number(message.id)
    const resolve = this.pending.get(id)
    if (resolve) {
      this.pending.delete(id)
      resolve(message)
    }
  }
}
