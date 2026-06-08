export type ResourceProcess = {
  pid?: number | string
  name: string
  user?: string
  command?: string
  raw_cpu_percent?: number
  normalized_cpu_percent?: number
  cpu_percent?: number
  memory_bytes?: number
  memory_percent?: number
  memory_mb?: number
  logical_cpu_count?: number
}

export type ResourceEventPayload = {
  event: 'ResourceUpdated'
  timestamp: number
  sampler_status: 'warming_up' | 'ready' | 'error' | string
  sampler_error?: string
  platform: string
  python_version?: string
  psutil_available?: boolean
  logical_cpu_count: number
  system_cpu_percent?: number
  memory: {
    total_bytes: number
    used_bytes: number
    percent?: number
  }
  disk: {
    mount: string
    total_bytes: number
    used_bytes: number
    percent?: number
  }
  top_cpu: ResourceProcess[]
  top_memory: ResourceProcess[]
  permission_denied_count?: number
  sample_age_ms?: number
  session?: Record<string, unknown>
}

export type ResourceValidation = {
  ok: boolean
  errors: string[]
}
