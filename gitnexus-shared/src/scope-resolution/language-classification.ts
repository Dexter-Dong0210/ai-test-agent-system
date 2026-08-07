/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2TUVvMWF3PT06ZDdkMzAyMjc=

/**
 * `LanguageClassification` — RFC §6.1 Ring 3 / Ring 4 governance.
 *
 * Classifies each `SupportedLanguages` member for the rollout. Ring 4 (DAG
 * retirement) is gated on *all production languages* being registry-primary
 * and stable for one release cycle; `experimental` and `quarantined`
 * languages do not block.
 *
 * Initial classification (locked in Ring 1 #910):
 *   - production: javascript, typescript, python, java, c, cpp, csharp, go,
 *                 ruby, rust, php, kotlin, swift, dart
 *   - experimental: vue (embedded-language / SFC complexity),
 *                   cobol (regex-provider path)
 *   - quarantined: (none)
 */

import { SupportedLanguages } from '../languages.js';

export type LanguageClassification = 'production' | 'experimental' | 'quarantined';

/**
 * The canonical classification for each supported language. Governance
 * changes (promote `experimental` → `production`, quarantine a language, …)
 * update this map in a dedicated PR.
 */
export const LanguageClassifications: Readonly<Record<SupportedLanguages, LanguageClassification>> =
  {
    [SupportedLanguages.JavaScript]: 'production',
    [SupportedLanguages.TypeScript]: 'production',
    [SupportedLanguages.Python]: 'production',
    [SupportedLanguages.Java]: 'production',
    [SupportedLanguages.C]: 'production',
    [SupportedLanguages.CPlusPlus]: 'production',
    [SupportedLanguages.CSharp]: 'production',
    [SupportedLanguages.Go]: 'production',
    [SupportedLanguages.Ruby]: 'production',
    [SupportedLanguages.Rust]: 'production',
    [SupportedLanguages.PHP]: 'production',
    [SupportedLanguages.Kotlin]: 'production',
    [SupportedLanguages.Swift]: 'production',
    [SupportedLanguages.Dart]: 'production',
    [SupportedLanguages.Vue]: 'experimental',
    [SupportedLanguages.Cobol]: 'experimental',
  };

/** Convenience predicate: is this language gating Ring 4 retirement? */
export function isProductionLanguage(lang: SupportedLanguages): boolean {
  return LanguageClassifications[lang] === 'production';
}
// TODO  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2TUVvMWF3PT06ZDdkMzAyMjc=
