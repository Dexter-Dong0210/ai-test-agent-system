/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

/**
 * `ORIGIN_PRIORITY` — RFC Appendix B (authoritative values).
 *
 * Tie-break ordering applied inside `Registry.lookup` Step 7 when
 * `|Δconfidence| < 0.001` between two `Resolution` candidates. Lower number
 * = stronger (wins the tie).
 *
 * Full tie-break order (§4.2 Step 7):
 *   confidence DESC → scope depth ASC → MRO depth ASC → ORIGIN_PRIORITY ASC
 *   → DefId.localeCompare
 */
// @ts-expect-error  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2WmtSNFRnPT06NGMyMTdmMzc=

export type OriginForTieBreak =
  | 'local'
  | 'import'
  | 'reexport'
  | 'namespace'
  | 'wildcard'
  | 'global-qualified'
  | 'global-name';
// eslint-disable  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2WmtSNFRnPT06NGMyMTdmMzc=

export const ORIGIN_PRIORITY: Readonly<Record<OriginForTieBreak, number>> = {
  local: 0,
  import: 1,
  reexport: 2,
  namespace: 3,
  wildcard: 4,
  'global-qualified': 5,
  'global-name': 6,
};
