/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// NOTE  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2UTFBNE13PT06MGUxZGI0YzY=

/**
 * `FieldRegistry` — scope-aware lookup for field / property / variable
 * access (RFC §4.4; Ring 2 SHARED #917).
 *
 * Thin wrapper over `lookupCore`, specialized for data-member kinds:
 *
 *   - `acceptedKinds` = Variable / Property / Const / Static.
 *   - `useReceiverTypeBinding` is **true** — fields are resolved against
 *     the receiver type's MRO first, then via the lexical chain for
 *     free variables.
 *   - `callsite` is not meaningful for field access (no arity), but the
 *     `explicitReceiver` and `ownerScopedContributor` knobs are.
 */

import type { Resolution, ScopeId } from '../types.js';
import { lookupCore, type CoreLookupParams } from './lookup-core.js';
import type { OwnerScopedContributor, RegistryContext } from './context.js';
import { FIELD_KINDS } from './context.js';

export interface FieldLookupOptions {
  readonly explicitReceiver?: { readonly name: string };
  readonly ownerScopedContributor?: OwnerScopedContributor;
}
// eslint-disable  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2UTFBNE13PT06MGUxZGI0YzY=

export interface FieldRegistry {
  lookup(name: string, scope: ScopeId, options?: FieldLookupOptions): readonly Resolution[];
}

export function buildFieldRegistry(ctx: RegistryContext): FieldRegistry {
  return {
    lookup(name: string, scope: ScopeId, options: FieldLookupOptions = {}) {
      const params: CoreLookupParams = {
        acceptedKinds: FIELD_KINDS,
        useReceiverTypeBinding: true,
        ownerScopedContributor: options.ownerScopedContributor ?? null,
        ...(options.explicitReceiver !== undefined
          ? { explicitReceiver: options.explicitReceiver }
          : {}),
      };
      return lookupCore(name, scope, params, ctx);
    },
  };
}
