import type { ResourceEventPayload, ResourceValidation } from '../types/resourceEvent.js'

const REQUIRED = ['event', 'timestamp', 'sampler_status', 'platform', 'logical_cpu_count', 'memory', 'disk', 'top_cpu', 'top_memory']

export function validateResourceEvent(value: unknown): ResourceValidation {
  const payload = readObject(value)
  const errors: string[] = []
  for (const key of REQUIRED) {
    if (!(key in payload)) {
      errors.push(`missing ${key}`)
    }
  }
  const memory = readObject(payload.memory)
  const disk = readObject(payload.disk)
  for (const key of ['total_bytes', 'used_bytes']) {
    if (typeof memory[key] !== 'number') {
      errors.push(`missing memory.${key}`)
    }
    if (typeof disk[key] !== 'number') {
      errors.push(`missing disk.${key}`)
    }
  }
  if (!Array.isArray(payload.top_cpu)) {
    errors.push('top_cpu must be list')
  }
  if (!Array.isArray(payload.top_memory)) {
    errors.push('top_memory must be list')
  }
  return { ok: errors.length === 0, errors }
}

export function normalizeResourceEvent(value: unknown): Record<string, unknown> {
  const payload = readObject(value)
  const memory = readObject(payload.memory)
  const disk = readObject(payload.disk)
  const logicalCpuCount = numberValue(payload.logical_cpu_count) ?? numberValue(readObject(payload.system).logical_cpu_count) ?? 1
  const normalized: Record<string, unknown> = {
    ...payload,
    system: {
      ...readObject(payload.system),
      cpu_percent: numberValue(payload.system_cpu_percent) ?? numberValue(readObject(payload.system).cpu_percent),
      system_cpu_percent: numberValue(payload.system_cpu_percent) ?? numberValue(readObject(payload.system).system_cpu_percent),
      logical_cpu_count: logicalCpuCount,
      sampler_status: payload.sampler_status,
      sampler_error: payload.sampler_error,
      memory_used_gb: bytesToGb(memory.used_bytes),
      memory_total_gb: bytesToGb(memory.total_bytes),
      memory_bytes: memory.used_bytes,
      memory_total_bytes: memory.total_bytes,
      memory_percent: memory.percent,
    },
    disk: {
      ...disk,
      mountpoint: disk.mount,
      used_gb: bytesToGb(disk.used_bytes),
      total_gb: bytesToGb(disk.total_bytes),
      percent: disk.percent,
    },
    top_cpu_processes: Array.isArray(payload.top_cpu) ? payload.top_cpu : payload.top_cpu_processes,
    top_memory_processes: Array.isArray(payload.top_memory) ? payload.top_memory : payload.top_memory_processes,
    resource_schema: validateResourceEvent(payload),
  }
  return normalized as ResourceEventPayload & Record<string, unknown>
}

function readObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {}
}

function numberValue(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function bytesToGb(value: unknown): number | undefined {
  const number = numberValue(value)
  return number === undefined ? undefined : number / 1024 / 1024 / 1024
}
