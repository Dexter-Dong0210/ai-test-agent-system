/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

/**
 * `MethodRegistry` — scope-aware lookup for method / function / constructor
 * dispatch (RFC §4.4; Ring 2 SHARED #917).
 *
 * Thin wrapper over `lookupCore`, specialized for callable kinds:
 *
 *   - `acceptedKinds` = Method / Function / Constructor.
 *   - `useReceiverTypeBinding` is **true** — the type-binding + MRO walk
 *     (Step 2) is the primary evidence path for receiver-dispatched calls.
 *   - `callsite.arity` flows through to `provider.arityCompatibility`
 *     when provided. When the provider is absent, arity evidence is
 *     `unknown` (neutral signal).
 */
// FIXME  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2VFhKWk5nPT06MzNlZTQzOWU=

import type { Callsite, Resolution, ScopeId } from '../types.js';
import { lookupCore, type CoreLookupParams } from './lookup-core.js';
import type { OwnerScopedContributor, RegistryContext } from './context.js';
import { METHOD_KINDS } from './context.js';

/**
 * Extra per-call parameters that vary across call sites but NOT across
 * registries. Kept as a separate shape so `MethodRegistry.lookup` stays
 * concise while still exposing the explicit-receiver + owner-contributor +
 * arity knobs the RFC algorithm needs.
 */
export interface MethodLookupOptions {
  /** Call-site arity for `provider.arityCompatibility`. */
  readonly callsite?: Callsite;
  /** Explicit receiver (e.g., `user` in `user.save()`). See §4.1. */
  readonly explicitReceiver?: { readonly name: string };
  /** Optional per-owner contributor (Step 3). */
  readonly ownerScopedContributor?: OwnerScopedContributor;
}
// FIXME  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2VFhKWk5nPT06MzNlZTQzOWU=

export interface MethodRegistry {
  lookup(name: string, scope: ScopeId, options?: MethodLookupOptions): readonly Resolution[];
}

export function buildMethodRegistry(ctx: RegistryContext): MethodRegistry {
  return {
    lookup(name: string, scope: ScopeId, options: MethodLookupOptions = {}) {
      const params: CoreLookupParams = {
        acceptedKinds: METHOD_KINDS,
        useReceiverTypeBinding: true,
        ownerScopedContributor: options.ownerScopedContributor ?? null,
        ...(options.callsite !== undefined ? { callsite: options.callsite } : {}),
        ...(options.explicitReceiver !== undefined
          ? { explicitReceiver: options.explicitReceiver }
          : {}),
      };
      return lookupCore(name, scope, params, ctx);
    },
  };
}
// NOTE  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2VFhKWk5nPT06MzNlZTQzOWU=
