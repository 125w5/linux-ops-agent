import React, { useMemo } from 'react'
import { Box, Text } from 'ink'
import type { Message } from '../state/events.js'
import type { ScrollState } from '../state/scrollState.js'
import { messagesToVirtualLines, visibleVirtualLines } from '../utils/virtualLines.js'
import { searchMessages } from './MessageSearch.js'

export function ConversationViewport({
  messages,
  scroll,
  height,
  width,
  searchTerm,
}: {
  messages: Message[]
  scroll: ScrollState
  height: number
  width: number
  searchTerm?: string
}): React.ReactElement {
  const visibleMessages = searchTerm ? searchMessages(messages, searchTerm) : messages
  const lines = useMemo(() => messagesToVirtualLines(visibleMessages, Math.max(24, width - 2)), [visibleMessages, width])
  const visible = visibleVirtualLines(lines, searchTerm ? 0 : scroll.offset, height)

  return <Box flexDirection="column" height={height} overflow="hidden">
    {searchTerm ? <Text color="yellow">Search: {searchTerm} ({lines.length} visible lines)</Text> : null}
    {visible.map(line => <Text key={line.key} color={roleColor(line.role)}>{line.text}</Text>)}
    {visible.length < height ? emptyRows(height - visible.length - (searchTerm ? 1 : 0)) : null}
  </Box>
}

function emptyRows(count: number): React.ReactElement[] {
  return Array.from({ length: Math.max(0, count) }, (_, index) => <Text key={`empty-${index}`}> </Text>)
}

function roleColor(role: Message['role']): string {
  if (role === 'assistant') return 'cyan'
  if (role === 'user') return 'green'
  if (role === 'tool') return 'yellow'
  return 'gray'
}
