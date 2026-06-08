import React from 'react'
import { Box, Text } from 'ink'

const FIELDS = [
  'input_received_ms',
  'placeholder_painted_ms',
  'fast_router_ms',
  'local_plan_ms',
  'api_call_count',
  'api_call_start_ms',
  'api_first_token_ms',
  'api_total_ms',
  'tool_run_ms',
  'local_summary_ms',
  'report_write_ms',
  'total_turn_ms',
  'fallback_reason',
]

export function LatencyPanel({ trace }: { trace?: Record<string, unknown> | null }): React.ReactElement {
  const data = trace ?? {}
  return <Box flexDirection="column">
    <Text color="cyan">Latency Trace</Text>
    {FIELDS.map(field => <Text key={field}>{field}: {String(data[field] ?? 0)}</Text>)}
  </Box>
}
