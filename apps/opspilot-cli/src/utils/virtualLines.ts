import type { Message } from '../state/events.js'

export type VirtualLine = {
  key: string
  text: string
  role: Message['role']
}

export function messageToVirtualLines(message: Message, index: number, width = 80): VirtualLine[] {
  const prefix = roleLabel(message.role)
  const content = message.content || ''
  const wrapped = wrapText(`${prefix} ${content}`, Math.max(20, width))
  return wrapped.map((text, lineIndex) => ({
    key: `${index}-${lineIndex}`,
    text,
    role: message.role,
  }))
}

export function messagesToVirtualLines(messages: Message[], width = 80): VirtualLine[] {
  return messages.flatMap((message, index) => messageToVirtualLines(message, index, width))
}

export function visibleVirtualLines(lines: VirtualLine[], offset: number, height: number): VirtualLine[] {
  return lines.slice(Math.max(0, offset), Math.max(0, offset) + Math.max(1, height))
}

function wrapText(text: string, width: number): string[] {
  const lines: string[] = []
  for (const rawLine of text.split(/\r?\n/)) {
    if (!rawLine) {
      lines.push('')
      continue
    }
    for (let index = 0; index < rawLine.length; index += width) {
      lines.push(rawLine.slice(index, index + width))
    }
  }
  return lines
}

function roleLabel(role: Message['role']): string {
  if (role === 'assistant') return 'assistant'
  if (role === 'user') return 'you'
  if (role === 'tool') return 'tool'
  return 'system'
}
