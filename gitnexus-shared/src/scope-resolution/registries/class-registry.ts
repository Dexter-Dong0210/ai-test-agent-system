/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

/**
 * `ClassRegistry` — scope-aware lookup for class-like symbols
 * (RFC §4.4; Ring 2 SHARED #917).
 *
 * Thin wrapper over `lookupCore`, specialized for class kinds:
 *
 *   - `acceptedKinds` = Class / Interface / Enum / Struct / Union /
 *     Trait / TypeAlias / Typedef / Record / Delegate / Annotation /
 *     Template / Namespace.
 *   - `useReceiverTypeBinding` is **false** — classes are resolved by
 *     name through the lexical chain + global qualified fallback, not
 *     via a receiver type.
 *   - Arity filter is not applicable (classes are not called with
 *     argument counts at lookup time).
 */
// FIXME  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2YTFGcVl3PT06ODAwMWZkNGM=

import type { Resolution, ScopeId } from '../types.js';
import { lookupCore, type CoreLookupParams } from './lookup-core.js';
import { CLASS_KINDS, type RegistryContext } from './context.js';

export interface ClassRegistry {
  /**
   * Look up a class-like symbol by simple or dotted name anchored at
   * `scope`. Returns a confidence-ranked `Resolution[]`; consume `[0]`
   * for the best answer.
   */
  lookup(name: string, scope: ScopeId): readonly Resolution[];
}
// TODO  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2YTFGcVl3PT06ODAwMWZkNGM=

export function buildClassRegistry(ctx: RegistryContext): ClassRegistry {
  const params: CoreLookupParams = {
    acceptedKinds: CLASS_KINDS,
    useReceiverTypeBinding: false,
    ownerScopedContributor: null,
  };
  return {
    lookup(name: string, scope: ScopeId) {
      return lookupCore(name, scope, params, ctx);
    },
  };
}
