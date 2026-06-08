import React from 'react'
import { Box, Text } from 'ink'
import { SandboxProfileCard } from '../components/SandboxProfileCard.js'

const PROFILES = [
  { name: 'safe-read', description: 'Only safe read-only observation commands.', allow: ['safe-read'], ask: [], deny: ['write', 'dangerous'], examples: ['df -h', 'ps aux'] },
  { name: 'ops-read', description: 'Read configs, logs, docker state, and validation commands.', allow: ['safe-read'], ask: ['low-risk'], deny: ['dangerous'], examples: ['journalctl', 'nginx -t'] },
  { name: 'lab-write', description: 'Low-risk writes only inside sandbox workflows.', allow: ['safe-read'], ask: ['low-risk'], deny: ['dangerous'], examples: ['fault-lab'] },
  { name: 'admin-confirm', description: 'Ask before real low-risk operations; dangerous operations remain blocked.', allow: ['safe-read'], ask: ['low-risk'], deny: ['dangerous'], examples: ['kill -TERM <pid>'] },
]

export function PermissionsScreen({ current }: { current: string }): React.ReactElement {
  return <Box flexDirection="column">
    <Text color="cyan" bold>Permissions</Text>
    {PROFILES.map(profile => (
      <SandboxProfileCard key={profile.name} {...profile} description={`${profile.description}${profile.name === current ? ' (current)' : ''}`} />
    ))}
    <Text color="gray">Select with /permissions safe-read | ops-read | lab-write | admin-confirm.</Text>
  </Box>
}
