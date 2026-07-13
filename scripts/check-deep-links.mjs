#!/usr/bin/env node
/**
 * Sister platform deep-link rot check for Ariva District Life Pulse.
 *
 * Sends HEAD requests (GET fallback on 405) to FoodLK, Octane, and PropertyLK
 * homepage URLs from backend adapters (`food.py`, `fuel.py`, `property.py`).
 *
 * Usage:
 *   node scripts/check-deep-links.mjs
 *
 * Exit codes:
 *   0 — all targets responded (2xx/3xx) or failure rate is at most 10%
 *   1 — more than 10% of targets failed (network error or 4xx/5xx)
 *
 * Environment:
 *   DEEP_LINK_TIMEOUT_MS — per-request timeout in milliseconds (default: 10000)
 */

import { request as httpsRequest } from 'node:https'
import { request as httpRequest } from 'node:http'

const DEFAULT_TIMEOUT_MS = Number.parseInt(process.env.DEEP_LINK_TIMEOUT_MS ?? '10000', 10)

/** User-facing sister platform homepages (adapter `homepage_url` deep-link targets). */
const SISTER_PLATFORM_URLS = [
  { name: 'FoodLK homepage', url: 'https://food-platform-one.vercel.app' },
  { name: 'Octane homepage', url: 'https://octane-smoky.vercel.app' },
  { name: 'PropertyLK homepage', url: 'https://propertylk-one.vercel.app' },
]

const FAILURE_THRESHOLD = 0.1

/**
 * @param {string} url
 * @param {string} method
 * @param {number} timeoutMs
 * @returns {Promise<{ ok: boolean; status?: number; error?: string }>}
 */
function probeRequest(url, method, timeoutMs) {
  return new Promise((resolve) => {
    let settled = false
    const finish = (result) => {
      if (settled) return
      settled = true
      resolve(result)
    }

    try {
      const parsed = new URL(url)
      const requestFn = parsed.protocol === 'https:' ? httpsRequest : httpRequest
      const req = requestFn(
        parsed,
        { method, timeout: timeoutMs },
        (res) => {
          res.resume()
          const status = res.statusCode ?? 0
          finish({ ok: status >= 200 && status < 400, status })
        },
      )

      req.on('timeout', () => {
        req.destroy()
        finish({ ok: false, error: 'timeout' })
      })
      req.on('error', (error) => {
        finish({ ok: false, error: error.message })
      })
      req.end()
    } catch (error) {
      finish({ ok: false, error: error instanceof Error ? error.message : String(error) })
    }
  })
}

/**
 * @param {string} url
 * @param {number} timeoutMs
 * @returns {Promise<{ ok: boolean; status?: number; error?: string }>}
 */
async function checkUrl(url, timeoutMs) {
  const head = await probeRequest(url, 'HEAD', timeoutMs)
  if (head.ok || head.status !== 405) {
    return head
  }
  return probeRequest(url, 'GET', timeoutMs)
}

async function main() {
  const results = []

  for (const target of SISTER_PLATFORM_URLS) {
    const result = await checkUrl(target.url, DEFAULT_TIMEOUT_MS)
    results.push({ ...target, ...result })
    const detail = result.ok ? `OK (${result.status})` : `FAIL (${result.error ?? result.status})`
    console.log(`${result.ok ? '✓' : '✗'} ${target.name}: ${target.url} — ${detail}`)
  }

  const failed = results.filter((item) => !item.ok).length
  const failureRate = failed / results.length

  console.log(`\nChecked ${results.length} URLs; ${failed} failed (${(failureRate * 100).toFixed(1)}%).`)

  if (failureRate > FAILURE_THRESHOLD) {
    console.error(`Failure rate exceeds ${FAILURE_THRESHOLD * 100}% threshold.`)
    process.exit(1)
  }

  if (failed > 0) {
    console.warn(`Within ${FAILURE_THRESHOLD * 100}% tolerance; exiting successfully.`)
  } else {
    console.log('All sister platform deep links responded successfully.')
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})
