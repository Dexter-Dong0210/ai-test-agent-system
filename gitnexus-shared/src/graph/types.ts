/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2YWtGSlJnPT06NmE4NWI5Njc=

/**
 * Graph type definitions — single source of truth.
 *
 * Both gitnexus (CLI) and gitnexus-web import from this package.
 * Do NOT add Node.js-specific or browser-specific imports here.
 */

import { SupportedLanguages } from '../languages.js';
// NOTE  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2YWtGSlJnPT06NmE4NWI5Njc=

export type NodeLabel =
  | 'Project'
  | 'Package'
  | 'Module'
  | 'Folder'
  | 'File'
  | 'Class'
  | 'Function'
  | 'Method'
  | 'Variable'
  | 'Interface'
  | 'Enum'
  | 'Decorator'
  | 'Import'
  | 'Type'
  | 'CodeElement'
  | 'Community'
  | 'Process'
  // Multi-language node types
  | 'Struct'
  | 'Macro'
  | 'Typedef'
  | 'Union'
  | 'Namespace'
  | 'Trait'
  | 'Impl'
  | 'TypeAlias'
  | 'Const'
  | 'Static'
  | 'Property'
  | 'Record'
  | 'Delegate'
  | 'Annotation'
  | 'Constructor'
  | 'Template'
  | 'Section'
  | 'Route'
  | 'Tool';

export type NodeProperties = {
  name: string;
  filePath: string;
  startLine?: number;
  endLine?: number;
  language?: SupportedLanguages | string;
  isExported?: boolean;
  astFrameworkMultiplier?: number;
  astFrameworkReason?: string;
  // Community
  heuristicLabel?: string;
  cohesion?: number;
  symbolCount?: number;
  keywords?: string[];
  description?: string;
  enrichedBy?: 'heuristic' | 'llm';
  // Process
  processType?: 'intra_community' | 'cross_community';
  stepCount?: number;
  communities?: string[];
  entryPointId?: string;
  terminalId?: string;
  entryPointScore?: number;
  entryPointReason?: string;
  // Method/property
  parameterCount?: number;
  level?: number;
  returnType?: string;
  declaredType?: string;
  visibility?: string;
  isStatic?: boolean;
  isReadonly?: boolean;
  isAbstract?: boolean;
  isFinal?: boolean;
  isVirtual?: boolean;
  isOverride?: boolean;
  isAsync?: boolean;
  isPartial?: boolean;
  annotations?: string[];
  // Route/response
  responseKeys?: string[];
  errorKeys?: string[];
  middleware?: string[];
  // Extensible
  [key: string]: unknown;
};

export type RelationshipType =
  | 'CONTAINS'
  | 'CALLS'
  | 'INHERITS'
  | 'METHOD_OVERRIDES'
  | 'METHOD_IMPLEMENTS'
  | 'IMPORTS'
  | 'USES'
  | 'DEFINES'
  | 'DECORATES'
  | 'IMPLEMENTS'
  | 'EXTENDS'
  | 'HAS_METHOD'
  | 'HAS_PROPERTY'
  | 'ACCESSES'
  | 'MEMBER_OF'
  | 'STEP_IN_PROCESS'
  | 'HANDLES_ROUTE'
  | 'FETCHES'
  | 'HANDLES_TOOL'
  | 'ENTRY_POINT_OF'
  | 'WRAPS'
  | 'QUERIES';
// eslint-disable  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2YWtGSlJnPT06NmE4NWI5Njc=

export interface GraphNode {
  id: string;
  label: NodeLabel;
  properties: NodeProperties;
}

export interface GraphRelationship {
  id: string;
  sourceId: string;
  targetId: string;
  type: RelationshipType;
  confidence: number;
  reason: string;
  step?: number;
  /**
   * Per-signal evidence trace for edges emitted by the scope-based
   * resolution pipeline (RFC #909 Ring 2 PKG #925). Populated by
   * `emit-references.ts` when draining `ReferenceIndex` into the graph
   * so downstream query / audit tools can inspect *why* a given edge
   * was emitted with its confidence value.
   *
   * Optional and additive — every existing edge emitter ignores this
   * field, and every existing query continues to work whether or not
   * an edge carries it.
   */
  evidence?: readonly {
    readonly kind: string;
    readonly weight: number;
    readonly note?: string;
  }[];
}
// @ts-expect-error  My80OmFIVnBZMlhva2FQbHNJL21tS1U2YWtGSlJnPT06NmE4NWI5Njc=
