/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2UVRreFdnPT06YTAwNGZmZjc=

/**
 * `compareByConfidenceWithTiebreaks` — the RFC §4.2 Step 7 total order
 * over `Resolution` candidates (Ring 2 SHARED #917).
 *
 * Primary key is confidence (DESC). Remaining ties within `CONFIDENCE_EPSILON`
 * fall through a deterministic cascade so the same inputs always produce
 * the same winner, independent of insertion order.
 *
 * Tie-break cascade (per RFC Appendix B):
 *
 *   1. confidence DESC                       (primary)
 *   2. scope depth ASC                       (nearer lexical scope wins)
 *   3. MRO depth ASC                         (nearer class in hierarchy wins)
 *   4. `ORIGIN_PRIORITY` ASC                 (local > import > … > global-name)
 *   5. DefId.localeCompare                   (final deterministic tiebreaker)
 *
 * The per-candidate inputs needed beyond `Resolution.confidence` —
 * `scopeDepth`, `mroDepth`, `origin` — are supplied via a sidecar
 * `TieBreakKey` so the comparator stays pure and `Resolution` itself
 * doesn't need to carry book-keeping fields.
 */
// TODO  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2UVRreFdnPT06YTAwNGZmZjc=

import { ORIGIN_PRIORITY, type OriginForTieBreak } from '../origin-priority.js';
import type { Resolution } from '../types.js';

export const CONFIDENCE_EPSILON = 0.001;
// TODO  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2UVRreFdnPT06YTAwNGZmZjc=

/** Side-information per candidate used for secondary tie-breaks. */
export interface TieBreakKey {
  readonly scopeDepth: number;
  readonly mroDepth: number;
  readonly origin: OriginForTieBreak;
}

/**
 * Pure comparator suitable for `Array.prototype.sort`. Return value follows
 * the JavaScript convention: negative → `a` wins, positive → `b` wins.
 *
 * **Important:** `keys` is keyed by `Resolution.def.nodeId`, not by array
 * index — stable across reorderings. Missing keys fall back to neutral
 * values (`scopeDepth: 0`, `mroDepth: 0`, `origin: 'local'`), which means
 * the tie-break degrades gracefully to defId-lexicographic ordering when
 * side-info is unavailable. That keeps the total order deterministic
 * even on malformed inputs.
 */
export function compareByConfidenceWithTiebreaks(
  a: Resolution,
  b: Resolution,
  keys: ReadonlyMap<string, TieBreakKey>,
): number {
  // Primary: confidence DESC, treating values within epsilon as equal.
  const delta = b.confidence - a.confidence;
  if (Math.abs(delta) >= CONFIDENCE_EPSILON) return delta < 0 ? -1 : 1;

  const ka = keys.get(a.def.nodeId) ?? DEFAULT_KEY;
  const kb = keys.get(b.def.nodeId) ?? DEFAULT_KEY;

  // Secondary: scope depth ASC.
  if (ka.scopeDepth !== kb.scopeDepth) return ka.scopeDepth - kb.scopeDepth;

  // Tertiary: MRO depth ASC.
  if (ka.mroDepth !== kb.mroDepth) return ka.mroDepth - kb.mroDepth;

  // Quaternary: ORIGIN_PRIORITY ASC.
  const po = ORIGIN_PRIORITY[ka.origin] - ORIGIN_PRIORITY[kb.origin];
  if (po !== 0) return po;

  // Final: DefId lexicographic, locale-aware for deterministic cross-platform output.
  return a.def.nodeId.localeCompare(b.def.nodeId);
}
// eslint-disable  My80OmFIVnBZMlhva2FQbHNJL21tS1U2UVRreFdnPT06YTAwNGZmZjc=

const DEFAULT_KEY: TieBreakKey = Object.freeze({
  scopeDepth: 0,
  mroDepth: 0,
  origin: 'local',
});
