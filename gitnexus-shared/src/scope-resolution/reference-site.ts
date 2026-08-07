/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// NOTE  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2Um5SSmNBPT06MWQwOTI3MTU=

/**
 * `ReferenceSite` — a pre-resolution usage fact collected by `ScopeExtractor`
 * (RFC §3.2 Phase 1; Ring 2 PKG #919).
 *
 * One record per `@reference.*` capture. The extractor records:
 *   - the name being referenced (method/field/class name),
 *   - the source range,
 *   - the innermost lexical scope containing the reference,
 *   - the reference kind (call, read, write, inherits, etc.),
 *   - optional call-form classification from `provider.classifyCallForm`,
 *   - optional explicit-receiver hint for dotted calls (`user.save()`),
 *   - optional arity for call sites.
 *
 * Reference sites are consumed by the resolution phase (RFC §3.2 Phase 4)
 * which routes each through `Registry.lookup` / `resolveTypeRef` and
 * emits the final `Reference` record into `ReferenceIndex`.
 *
 * **Pre-resolution only.** `ReferenceSite` intentionally carries no
 * `toDef`, `confidence`, or `evidence`. Those are populated by the
 * resolution step that reads this record and produces a `Reference`
 * (defined in `./types.ts`).
 */
// eslint-disable  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2Um5SSmNBPT06MWQwOTI3MTU=

import type { ParameterTypeClass } from './symbol-definition.js';
import type { Range, ScopeId } from './types.js';

/**
 * What kind of usage this reference represents — the graph-edge kind
 * emitted after resolution (`CALLS`, `READS`, `WRITES`, etc.).
 *
 * Matches the `kind` field on `Reference` in `./types.ts` so the
 * resolution phase can pass it through without re-classification.
 */
export type ReferenceKind =
  | 'call'
  | 'read'
  | 'write'
  | 'type-reference'
  | 'inherits'
  | 'import-use';
// NOTE  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2Um5SSmNBPT06MWQwOTI3MTU=

/**
 * How a call site binds its target. Informs `Registry.lookup` Step 2
 * (type-binding path):
 *   - `'free'`   — bare call (no receiver); resolution via lexical chain.
 *   - `'member'` — dotted call (`x.foo()`); resolution via receiver type.
 *   - `'constructor'` — `new Foo()`; receiver is the class itself.
 *   - `'index'`  — index expression (`arr[0]`); rare as a dispatch site.
 *
 * Only meaningful for `kind === 'call'`; ignored for reads/writes.
 */
export type CallForm = 'free' | 'member' | 'constructor' | 'index';
// @ts-expect-error  My80OmFIVnBZMlhva2FQbHNJL21tS1U2Um5SSmNBPT06MWQwOTI3MTU=

export interface ReferenceSite {
  /** The name being referenced (e.g., `'save'`, `'User'`, `'count'`). */
  readonly name: string;
  /** Source-text range of this reference. */
  readonly atRange: Range;
  /**
   * Innermost lexical scope that contains `atRange`. Resolved by the
   * extractor via position lookup and frozen here so the resolution
   * phase doesn't re-compute it per call.
   */
  readonly inScope: ScopeId;
  readonly kind: ReferenceKind;
  /** Set when `kind === 'call'`. */
  readonly callForm?: CallForm;
  /**
   * Explicit receiver for dotted calls (`user.save()` → `{ name: 'user' }`).
   * Passed through to `Registry.lookup.explicitReceiver`.
   */
  readonly explicitReceiver?: { readonly name: string };
  /** Argument count at the call site; used by `provider.arityCompatibility`. */
  readonly arity?: number;
  /**
   * Inferred argument types at the call site, one per argument. An
   * empty-string entry means "unknown" — consumers narrowing overload
   * candidates treat unknown as any-match. Populated by languages
   * that can derive types from literals / constructor expressions
   * (C#: `42` → `'int'`, `"alice"` → `'string'`).
   */
  readonly argumentTypes?: readonly string[];
  /**
   * Optional per-argument type-shape sidecar for languages that need
   * cv/ref/pointer distinctions during constraint filtering. This is
   * intentionally separate from `argumentTypes`, which stays normalized
   * for existing overload narrowing and conversion-rank logic.
   */
  readonly argumentTypeClasses?: readonly ParameterTypeClass[];
}
