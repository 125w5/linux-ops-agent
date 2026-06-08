import React from 'react'
import { Text } from 'ink'

export function RiskBadge({ risk }: { risk: string }): React.ReactElement {
  const color = risk === 'blocked' || risk === 'high_risk' ? 'red' : risk === 'low_risk' ? 'yellow' : 'green'
  return <Text backgroundColor={color} color="black"> {risk} </Text>
}
