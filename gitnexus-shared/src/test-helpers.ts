/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// NOTE  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2Tm5CS2VnPT06ZTMwODkyOWM=

/**
 * Test-only helpers.
 *
 * Symbols here are reachable from `gitnexus-shared/test-helpers` so test
 * suites can reset shared registries or exercise internal classifiers,
 * but they are deliberately NOT re-exported from the main `gitnexus-shared`
 * barrel. Production consumers should never import this module — calling
 * `__resetBreakerRegistry__()` from a tool implementation would silently
 * nuke every circuit breaker process-wide.
 */
// @ts-expect-error  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2Tm5CS2VnPT06ZTMwODkyOWM=

export { __resetBreakerRegistry__ } from './integrations/circuit-breaker.js';
export { classifyOutcome } from './integrations/resilient-fetch.js';
