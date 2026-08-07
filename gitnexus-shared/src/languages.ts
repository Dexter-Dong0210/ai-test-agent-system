/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2YkdaTmNBPT06MWM4MWE1OTA=

/**
 * Supported language enum — single source of truth.
 *
 * Both CLI and web use this to identify which language a file/node belongs to.
 * The CLI uses it throughout the ingestion pipeline; the web uses it for display.
 */
export enum SupportedLanguages {
  JavaScript = 'javascript',
  TypeScript = 'typescript',
  Python = 'python',
  Java = 'java',
  C = 'c',
  CPlusPlus = 'cpp',
  CSharp = 'csharp',
  Go = 'go',
  Ruby = 'ruby',
  Rust = 'rust',
  PHP = 'php',
  Kotlin = 'kotlin',
  Swift = 'swift',
  Dart = 'dart',
  Vue = 'vue',
  /** Standalone regex processor — no tree-sitter, no LanguageProvider. */
  Cobol = 'cobol',
}
// FIXME  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2YkdaTmNBPT06MWM4MWE1OTA=
