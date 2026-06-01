export type ProcessRow = {
  name: string
  cpuPercent?: number
  memoryMb?: number
}

const FILLED = '█'
const EMPTY = '░'

export function readObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {}
}

export function numberValue(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

export function usageBar(value: unknown, width = 10): string {
  const percent = clampPercent(numberValue(value))
  if (percent === undefined) {
    return EMPTY.repeat(width)
  }
  const filled = Math.max(0, Math.min(width, Math.round(percent / 100 * width)))
  return `${FILLED.repeat(filled)}${EMPTY.repeat(width - filled)}`
}

export function percentLabel(value: unknown): string {
  const percent = clampPercent(numberValue(value))
  return percent === undefined ? 'n/a' : `${Math.round(percent)}%`
}

export function loadLabel(value: unknown): string {
  const load = Array.isArray(value) ? value.map(item => numberValue(item)).filter(item => item !== undefined) : []
  if (!load.length) {
    return 'load n/a'
  }
  return `load ${load.slice(0, 3).map(item => item.toFixed(2)).join(' ')}`
}

export function memoryLabel(system: Record<string, unknown>): string {
  const used = numberValue(system.memory_used_gb)
  const total = numberValue(system.memory_total_gb)
  if (used === undefined || total === undefined) {
    return 'n/a'
  }
  return `${formatGb(used)} / ${formatGb(total)}`
}

export function diskLabel(disk: Record<string, unknown>): string {
  const used = numberValue(disk.used_gb)
  const total = numberValue(disk.total_gb)
  const mount = String(disk.mountpoint ?? disk.device ?? 'disk')
  if (used === undefined || total === undefined) {
    return `${mount} n/a`
  }
  return `${mount} ${formatGb(used)} / ${formatGb(total)}`
}

export function processRows(processes: unknown, totalMemoryGb?: number): ProcessRow[] {
  if (!Array.isArray(processes)) {
    return []
  }
  return processes.slice(0, 3).map(item => {
    const row = readObject(item)
    const memoryMb = numberValue(row.memory_mb) ?? memoryMbFromPercent(row.memory_percent, totalMemoryGb)
    return {
      name: String(row.name ?? '?'),
      cpuPercent: numberValue(row.cpu_percent),
      memoryMb,
    }
  })
}

export function sparkline(values: unknown[], width = 12): string {
  const blocks = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
  const numbers = values.map(numberValue).filter(value => value !== undefined)
  if (!numbers.length) {
    return '·'.repeat(width)
  }
  const recent = numbers.slice(-width)
  return recent.map(value => blocks[Math.max(0, Math.min(blocks.length - 1, Math.round(clamp(value, 0, 100) / 100 * (blocks.length - 1))))]).join('')
}

export function formatProcessCpu(row: ProcessRow): string {
  return row.cpuPercent === undefined ? 'n/a' : `${row.cpuPercent.toFixed(1)}%`
}

export function formatProcessMem(row: ProcessRow): string {
  return row.memoryMb === undefined ? 'n/a' : `${Math.round(row.memoryMb)}M`
}

function memoryMbFromPercent(value: unknown, totalMemoryGb?: number): number | undefined {
  const percent = numberValue(value)
  if (percent === undefined || totalMemoryGb === undefined) {
    return undefined
  }
  return totalMemoryGb * 1024 * percent / 100
}

function formatGb(value: number): string {
  return `${value.toFixed(value >= 10 ? 0 : 1)}G`
}

function clampPercent(value: number | undefined): number | undefined {
  return value === undefined ? undefined : clamp(value, 0, 100)
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value))
}
