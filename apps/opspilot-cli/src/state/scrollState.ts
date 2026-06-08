export type ScrollState = {
  offset: number
  viewportHeight: number
  totalLines: number
  atBottom: boolean
}

export const initialScrollState: ScrollState = {
  offset: 0,
  viewportHeight: 12,
  totalLines: 0,
  atBottom: true,
}

export function clampScroll(offset: number, totalLines: number, viewportHeight: number): number {
  return Math.max(0, Math.min(offset, Math.max(0, totalLines - viewportHeight)))
}

export function scrollToLatest(totalLines: number, viewportHeight: number): ScrollState {
  return {
    offset: clampScroll(totalLines, totalLines, viewportHeight),
    viewportHeight,
    totalLines,
    atBottom: true,
  }
}

export function scrollBy(state: ScrollState, delta: number): ScrollState {
  const offset = clampScroll(state.offset + delta, state.totalLines, state.viewportHeight)
  return {
    ...state,
    offset,
    atBottom: offset >= Math.max(0, state.totalLines - state.viewportHeight),
  }
}
