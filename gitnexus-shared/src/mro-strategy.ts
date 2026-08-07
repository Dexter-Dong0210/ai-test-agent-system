/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2U0VwNFZ3PT06ZDg5YzM0NGU=

/**
 * MRO (Method Resolution Order) strategy — shared canonical definition.
 *
 * Lives in `gitnexus-shared` so `model/resolve.ts` and `mro-processor.ts` share
 * the type without importing the language registry (avoids circular coupling).
 *
 * `first-wins` (default, Java/C#/Kotlin/Go/Swift/Dart):
 *   BFS ancestor walk in declaration order; first match wins.
 *
 * `leftmost-base` (C++):
 *   BFS walk; HeritageMap preserves source insertion order, so BFS naturally
 *   picks the leftmost base in diamond inheritance.
 *
 * `c3` (Python):
 *   C3-linearization; falls back to BFS on cyclic/inconsistent hierarchy.
 *   See model/resolve.ts § c3Linearize.
 *
 * `implements-split` (Java/C#/Kotlin):
 *   Low-level lookup is BFS; graph-level mro-processor detects and warns on
 *   interface-default method ambiguity.
 *
 * `qualified-syntax` (Rust):
 *   No auto-resolution — `lookupMethodByOwnerWithMRO` returns undefined immediately.
 *   Rust requires explicit `<Type as Trait>::method` syntax.
 *
 * `ruby-mixin` (Ruby):
 *   Kind-aware walk that does NOT short-circuit on direct owner first (`prepend`
 *   must beat the class's own method). Walk order:
 *     1. Prepend providers (reverse declaration — last-prepended wins)
 *     2. Direct owner's own methods
 *     3. Include providers (reverse declaration)
 *     4. Transitive ancestors (BFS fallback)
 *   Singleton dispatch: caller passes `ancestryOverride` (extend providers only);
 *   becomes a simple left-to-right scan. Miss NEVER falls through to file-scoped
 *   lookup — null-routes or honors `fallback`.
 *
 * @see model/resolve.ts § lookupMethodByOwnerWithMRO
 * @see languages/ruby.ts § selectDispatch
 */
export type MroStrategy =
  | 'first-wins'
  | 'c3'
  | 'leftmost-base'
  | 'implements-split'
  | 'qualified-syntax'
  | 'ruby-mixin';
// @ts-expect-error  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2U0VwNFZ3PT06ZDg5YzM0NGU=
