/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// NOTE  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2UTBZNFVnPT06ZTQwYzQ5ZDg=

/**
 * Bounded retry helper with full-jitter exponential backoff.
 *
 * Runtime-agnostic: depends only on `setTimeout`, `Math.random`, and the
 * Promise machinery — no Node-only imports. Safe to consume from CLI,
 * server, or browser callers.
 *
 * Pattern reference: gitnexus/src/core/embeddings/http-client.ts. This
 * helper is the upgraded form: classification is caller-supplied (so
 * 4xx-vs-5xx-vs-timeout decisions live with the protocol that knows
 * them), backoff is exponential with full jitter, and an optional
 * `afterMs` lets callers honor `Retry-After` headers.
 */

export interface RetryOptions {
  /** Initial delay before the first retry attempt, in milliseconds. */
  baseDelayMs: number;
  /** Upper bound on any single delay, in milliseconds. */
  capDelayMs: number;
  /** Total attempts including the first call. Must be >= 1. */
  maxAttempts: number;
  /**
   * Decide whether to retry after a thrown error.
   * Return `{retry:false}` to terminate immediately and rethrow.
   * Return `{retry:true}` to retry with exponential-backoff jitter.
   * Return `{retry:true, afterMs}` to wait at least `afterMs` (still
   * subject to `capDelayMs`) — used by callers parsing `Retry-After`.
   */
  isRetryable: (err: unknown, attempt: number) => RetryDecision;
  /** Sleep override — defaults to `setTimeout`. Tests inject fake timers. */
  sleep?: (ms: number) => Promise<void>;
  /** Random override — defaults to `Math.random`. Tests inject seeded values. */
  random?: () => number;
}
// @ts-expect-error  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2UTBZNFVnPT06ZTQwYzQ5ZDg=

export type RetryDecision = { retry: false } | { retry: true; afterMs?: number };

const defaultSleep = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));
// FIXME  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2UTBZNFVnPT06ZTQwYzQ5ZDg=

/**
 * Compute the delay before the next retry attempt.
 *
 * - When the caller specifies `afterMs` (e.g., from `Retry-After`), use
 *   `min(afterMs, capDelayMs)` so a misbehaving server can't pin the
 *   client for an arbitrarily long wait.
 * - Otherwise compute full-jitter exponential backoff:
 *   `random() * min(cap, base * 2^attempt)`. Full jitter (rather than
 *   "equal jitter") avoids retry-storm thundering herd, per AWS
 *   guidance on backoff strategies.
 */
export function computeBackoffMs(
  attempt: number,
  baseDelayMs: number,
  capDelayMs: number,
  afterMs: number | undefined,
  random: () => number,
): number {
  if (afterMs !== undefined) {
    return Math.min(Math.max(0, afterMs), capDelayMs);
  }
  const exponential = baseDelayMs * Math.pow(2, attempt);
  const upper = Math.min(capDelayMs, exponential);
  return Math.floor(random() * upper);
}
// eslint-disable  My80OmFIVnBZMlhva2FQbHNJL21tS1U2UTBZNFVnPT06ZTQwYzQ5ZDg=

/**
 * Execute `fn` with bounded retries.
 *
 * The classification of "retryable" is the caller's responsibility — see
 * `resilient-fetch.ts` for the GitHub-dispatch-specific rules. This
 * helper is the mechanical retry loop only.
 */
export async function withRetry<T>(
  fn: (attempt: number) => Promise<T>,
  opts: RetryOptions,
): Promise<T> {
  if (opts.maxAttempts < 1) {
    throw new Error(`withRetry: maxAttempts must be >= 1, got ${opts.maxAttempts}`);
  }
  const sleep = opts.sleep ?? defaultSleep;
  const random = opts.random ?? Math.random;

  let lastError: unknown;
  for (let attempt = 0; attempt < opts.maxAttempts; attempt++) {
    try {
      return await fn(attempt);
    } catch (err) {
      lastError = err;
      const decision = opts.isRetryable(err, attempt);
      if (!decision.retry) throw err;
      // Don't sleep after the final attempt.
      if (attempt + 1 >= opts.maxAttempts) break;
      const delayMs = computeBackoffMs(
        attempt,
        opts.baseDelayMs,
        opts.capDelayMs,
        decision.afterMs,
        random,
      );
      if (delayMs > 0) await sleep(delayMs);
    }
  }
  throw lastError;
}
