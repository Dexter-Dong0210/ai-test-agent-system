/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// NOTE  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2ZUVGcU53PT06M2Q3MWU4NDk=

/**
 * `SymbolDefinition` — the canonical shape of an indexed symbol record.
 *
 * Historically defined in `gitnexus/src/core/ingestion/model/symbol-table.ts`;
 * moved into `gitnexus-shared` as part of RFC #909 Ring 1 (#910) so the
 * scope-resolution types that reference it can live in the shared package
 * alongside their consumers (`gitnexus/` and `gitnexus-web/`).
 *
 * Shape is unchanged from the prior local definition.
 */

import type { NodeLabel } from '../graph/types.js';
// @ts-expect-error  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2ZUVGcU53PT06M2Q3MWU4NDk=

export interface ParameterTypeClass {
  /** Normalized base type, matching the coarse `parameterTypes` vocabulary when known. */
  base: string;
  /** Top-level cv signal preserved from the original C++ parameter spelling. */
  cv: 'none' | 'const' | 'volatile' | 'const volatile' | 'unknown';
  /** Coarse value/reference/pointer shape. */
  indirection: 'value' | 'lvalue-ref' | 'rvalue-ref' | 'pointer' | 'unknown';
  /** Number of pointer markers when indirection is `pointer`; otherwise 0. */
  pointerDepth: number;
}
// FIXME  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2ZUVGcU53PT06M2Q3MWU4NDk=

export interface SymbolDefinition {
  nodeId: string;
  filePath: string;
  type: NodeLabel;
  /** Canonical dot-separated qualified type name for class-like symbols
   *  (e.g. `App.Models.User`). Falls back to the simple symbol name when no
   *  package/namespace/module scope exists or no explicit qualified metadata is provided. */
  qualifiedName?: string;
  parameterCount?: number;
  /** Number of required (non-optional, non-default) parameters.
   *  Enables range-based arity filtering: argCount >= requiredParameterCount && argCount <= parameterCount. */
  requiredParameterCount?: number;
  /** Per-parameter type names for overload disambiguation (e.g. ['int', 'String']).
   *  Populated when parameter types are resolvable from AST (any typed language). */
  parameterTypes?: string[];
  /** Additive per-parameter type shape sidecar for languages that need cv/ref/pointer distinctions.
   *  Does not participate in graph node identity unless a resolver explicitly opts in. */
  parameterTypeClasses?: ParameterTypeClass[];
  /** Raw return type text extracted from AST (e.g. 'User', 'Promise<User>') */
  returnType?: string;
  /** Declared type for non-callable symbols — fields/properties (e.g. 'Address', 'List<User>') */
  declaredType?: string;
  /** Generic/template specialization arguments for class-like symbols (e.g. ['User'], ['T*']). */
  templateArguments?: string[];
  /** Per-language constraint payload for template / generic overloads
   *  (e.g. C++ `enable_if_t<P, T>` predicate trees, C++20 `requires` clauses).
   *  Opaque to shared code — the producing language adapter owns the shape
   *  and is the only consumer. Read via the optional
   *  `ScopeResolver.constraintCompatibility` hook during overload narrowing.
   *  Absent for symbols that have no constraints (the common case). */
  templateConstraints?: unknown;
  /** Links Method/Constructor/Property to owning Class/Struct/Trait nodeId */
  ownerId?: string;
}
