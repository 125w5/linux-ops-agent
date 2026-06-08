import React from 'react'
import { Box, Text } from 'ink'

export function TelemetryDoctorPanel({ doctor }: { doctor?: Record<string, unknown> | null }): React.ReactElement {
  if (!doctor) {
    return <Text color="gray">Run /monitor doctor to inspect telemetry.</Text>
  }
  const schema = readObject(doctor.schema)
  const errors = Array.isArray(schema.errors) ? schema.errors.map(String) : []
  return <Box flexDirection="column">
    <Text color="cyan">Telemetry Doctor</Text>
    <Text>platform: {String(doctor.platform ?? 'unknown')}</Text>
    <Text>python: {String(doctor.python_version ?? 'unknown')}</Text>
    <Text>psutil: {String(doctor.psutil_available ?? false)}</Text>
    <Text>cpus: {String(doctor.logical_cpu_count ?? 'unknown')}</Text>
    <Text>sampler: {String(doctor.sampler_status ?? 'unknown')}</Text>
    {doctor.sampler_error ? <Text color="red">error: {String(doctor.sampler_error)}</Text> : null}
    <Text>sample age: {String(doctor.last_sample_age_ms ?? 'unknown')}ms</Text>
    <Text>cpu: {String(doctor.system_cpu_percent ?? 'n/a')}</Text>
    <Text>top cpu/mem: {String(doctor.top_cpu_count ?? 0)} / {String(doctor.top_memory_count ?? 0)}</Text>
    <Text>frontend ResourceUpdated: {String(doctor.frontend_received_resource_updated ? 'yes' : 'no')}</Text>
    <Text color={errors.length ? 'red' : 'green'}>schema: {errors.length ? errors.join('; ') : 'ok'}</Text>
  </Box>
}

function readObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {}
}
