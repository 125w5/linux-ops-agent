export type Viewport = {
  width: number
  height: number
  compact: boolean
  showSidePanel: boolean
  headerHeight: number
  monitorHeight: number
  actionHeight: number
  inputHeight: number
  bodyHeight: number
  conversationWidth: number
  sideWidth: number
}

export function currentViewport(): Viewport {
  return makeViewport(process.stdout.columns || 100, process.stdout.rows || 30)
}

export function makeViewport(width: number, height: number): Viewport {
  const compact = height < 22 || width < 90
  const showSidePanel = width >= 110
  const headerHeight = 1
  const monitorHeight = compact ? 3 : 5
  const actionHeight = 3
  const inputHeight = 1
  const bodyHeight = Math.max(6, height - headerHeight - monitorHeight - actionHeight - inputHeight)
  const sideWidth = showSidePanel ? Math.max(42, Math.min(72, Math.floor(width * 0.36))) : 0
  const conversationWidth = Math.max(30, width - sideWidth - 3)
  return { width, height, compact, showSidePanel, headerHeight, monitorHeight, actionHeight, inputHeight, bodyHeight, conversationWidth, sideWidth }
}
