import React from 'react'
import type { Message } from '../state/events.js'
import { initialScrollState, type ScrollState } from '../state/scrollState.js'
import { ConversationViewport } from './ConversationViewport.js'

export function ConversationPane({
  messages,
  searchTerm,
  scroll,
  height = 12,
  width = 80,
}: {
  messages: Message[]
  searchTerm?: string
  scroll?: ScrollState
  height?: number
  width?: number
}): React.ReactElement {
  return <ConversationViewport messages={messages} searchTerm={searchTerm} scroll={scroll ?? initialScrollState} height={height} width={width} />
}
