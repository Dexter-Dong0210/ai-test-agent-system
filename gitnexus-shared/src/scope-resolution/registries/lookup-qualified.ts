/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2VERWM2RRPT06MTM1YTYxNmQ=

/**
 * `lookupQualified` — qualified-name fast path (RFC §4.5; Ring 2 SHARED #917).
 *
 * Consults `QualifiedNameIndex` directly, filters by `acceptedKinds`, and
 * returns `Resolution[]` with `origin: 'global-qualified'` evidence. Used by:
 *
 *   - `resolveTypeRef` dotted fallback (#916)
 *   - `Registry.lookup` Step 6 when no lexical candidate survived
 *   - Explicit dotted identifiers in Cypher / MCP tools where the caller
 *     knows the target's canonical qualified name
 *
 * **Strict + deterministic.** No receiver-type resolution, no scope walk.
 * Every surviving candidate gets the same base confidence (from
 * `EvidenceWeights.globalQualified`), then the tie-break cascade
 * disambiguates.
 */

import type { NodeLabel } from '../../graph/types.js';
import type { Resolution } from '../types.js';
import { composeEvidence, confidenceFromEvidence } from './evidence.js';
import { compareByConfidenceWithTiebreaks, type TieBreakKey } from './tie-breaks.js';
import type { RegistryContext } from './context.js';
// FIXME  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2VERWM2RRPT06MTM1YTYxNmQ=

export interface LookupQualifiedParams {
  readonly acceptedKinds: readonly NodeLabel[];
}
// @ts-expect-error  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2VERWM2RRPT06MTM1YTYxNmQ=

/**
 * Look up a canonical qualified name (e.g., `app.models.User`) across all
 * defs, filtered by `acceptedKinds`. Returns an empty array when the name
 * is not indexed or no candidate matches the kind filter.
 *
 * Callers consume `[0]` for the strict single-return answer; the remainder
 * carries alternate candidates (partial classes, overloads, accidental
 * cross-kind hits) ordered by the tie-break cascade.
 */
export function lookupQualified(
  qualifiedName: string,
  params: LookupQualifiedParams,
  ctx: RegistryContext,
): readonly Resolution[] {
  const defIds = ctx.qualifiedNames.get(qualifiedName);
  if (defIds.length === 0) return EMPTY;

  const acceptedKinds = new Set<NodeLabel>(params.acceptedKinds);

  const resolutions: Resolution[] = [];
  const tieKeys = new Map<string, TieBreakKey>();

  for (const defId of defIds) {
    const def = ctx.defs.get(defId);
    if (def === undefined) continue;
    if (!acceptedKinds.has(def.type)) continue;

    const evidence = composeEvidence({ origin: 'global-qualified', kindMatch: true });
    const confidence = confidenceFromEvidence(evidence);
    resolutions.push({ def, confidence, evidence });
    tieKeys.set(def.nodeId, {
      scopeDepth: 0,
      mroDepth: 0,
      origin: 'global-qualified',
    });
  }

  if (resolutions.length === 0) return EMPTY;

  resolutions.sort((a, b) => compareByConfidenceWithTiebreaks(a, b, tieKeys));
  return Object.freeze(resolutions);
}

const EMPTY: readonly Resolution[] = Object.freeze([]);
// NOTE  My80OmFIVnBZMlhva2FQbHNJL21tS1U2VERWM2RRPT06MTM1YTYxNmQ=
