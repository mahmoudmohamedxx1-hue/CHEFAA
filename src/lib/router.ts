'use client'
// Path-based routing with shareable URLs (/product/x, /category/x, ...)
// Keeps full backward compatibility with the legacy hash routes (#/p/x, #/c/x, ...)
// by remapping old segments to the new clean paths.

// legacy hash segment -> new path segment
const SEGMENT_MAP: Record<string, string> = {
  p: 'product',
  c: 'category',
  success: 'order-success',
}

/** Normalize any legacy/hash target into a clean app path. */
export function normalizePath(to: string): string {
  if (typeof to !== 'string' || !to) return '/'
  let path = to.startsWith('#') ? to.slice(1) : to
  if (!path.startsWith('/')) path = '/' + path

  const qi = path.indexOf('?')
  const query = qi >= 0 ? path.slice(qi) : ''
  const head = (qi >= 0 ? path.slice(0, qi) : path).replace(/\/+$/, '')
  const segs = head.split('/')
  if (segs.length > 1 && SEGMENT_MAP[segs[1]]) segs[1] = SEGMENT_MAP[segs[1]]
  return (segs.join('/') || '/') + query
}

// The Next.js router push function is captured here so the imperative `go()`
// helper can trigger client-side navigation from anywhere (event handlers, etc.)
// without a full page reload.
let routerPush: ((path: string, scroll?: boolean) => void) | null = null

export function bindRouter(push: (path: string, scroll?: boolean) => void) {
  routerPush = push
}

/** Navigate to a route. Accepts new paths (/product/x) and legacy hash paths (#/p/x). */
export const go = (to: string) => {
  const path = normalizePath(to)
  if (routerPush) routerPush(path)
  else if (typeof window !== 'undefined') window.location.assign(path)
}
