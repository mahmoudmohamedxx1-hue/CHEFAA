'use client'
import { useState, useEffect, useCallback } from 'react'

export interface Route {
  view: string
  params: string[]
  query: Record<string, string>
}

function parse(): Route {
  const raw = window.location.hash.replace(/^#\/?/, '')
  const [pathPart, queryPart] = raw.split('?')
  const segs = pathPart.split('/').filter(Boolean)
  const query: Record<string, string> = {}
  if (queryPart) {
    for (const kv of queryPart.split('&')) {
      const [k, v] = kv.split('=')
      if (k) query[decodeURIComponent(k)] = decodeURIComponent(v || '')
    }
  }
  return { view: segs[0] || 'home', params: segs.slice(1), query }
}

export function useHashRoute(): [Route, (to: string) => void] {
  const [route, setRoute] = useState<Route>({ view: 'home', params: [], query: {} })

  useEffect(() => {
    const update = () => {
      setRoute(parse())
      window.scrollTo({ top: 0 })
    }
    update()
    window.addEventListener('hashchange', update)
    return () => window.removeEventListener('hashchange', update)
  }, [])

  const nav = useCallback((to: string) => {
    const target = to.startsWith('#') ? to : `#${to.startsWith('/') ? to : '/' + to}`
    if (window.location.hash === target) {
      // same route: force re-parse (e.g. new search)
      setRoute(parse())
      window.scrollTo({ top: 0 })
    } else {
      window.location.hash = target
    }
  }, [])

  return [route, nav]
}

export const go = (to: string) => {
  window.location.hash = to.startsWith('#') ? to : `#${to.startsWith('/') ? to : '/' + to}`
}
