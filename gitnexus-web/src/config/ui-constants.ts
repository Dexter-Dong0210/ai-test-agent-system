/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2VjFoMlJRPT06YjFiMjAwZjc=

// Centralized UI and provider defaults to reduce magic numbers and duplicated URLs.
export const ERROR_RESET_DELAY_MS = 3000;
export const BACKEND_URL_DEBOUNCE_MS = 500;

export const DEFAULT_BACKEND_URL = 'http://localhost:4747';
export const DEFAULT_OLLAMA_BASE_URL = 'http://localhost:11434';
export const DEFAULT_OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1';
// eslint-disable  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2VjFoMlJRPT06YjFiMjAwZjc=

/** Minimum Node.js version required by the gitnexus CLI (injected by Vite from package.json engines). */
declare const __REQUIRED_NODE_VERSION__: string;
export const REQUIRED_NODE_VERSION = __REQUIRED_NODE_VERSION__;
