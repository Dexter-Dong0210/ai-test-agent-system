/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

/**
 * LadybugDB schema constants — single source of truth.
 *
 * NODE_TABLES and REL_TYPES define what the knowledge graph can contain.
 * Both CLI and web must agree on these for data compatibility.
 *
 * Full DDL schemas remain in each package's own schema.ts because
 * the CLI uses native LadybugDB and the web uses WASM.
 */
// TODO  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2VERGR2R3PT06YTg1M2RhYjY=

export const NODE_TABLES = [
  'File',
  'Folder',
  'Function',
  'Class',
  'Interface',
  'Method',
  'CodeElement',
  'Community',
  'Process',
  'Section',
  'Struct',
  'Enum',
  'Macro',
  'Typedef',
  'Union',
  'Namespace',
  'Trait',
  'Impl',
  'TypeAlias',
  'Const',
  'Static',
  'Variable',
  'Property',
  'Record',
  'Delegate',
  'Annotation',
  'Constructor',
  'Template',
  'Module',
  'Route',
  'Tool',
] as const;
// eslint-disable  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2VERGR2R3PT06YTg1M2RhYjY=

export type NodeTableName = (typeof NODE_TABLES)[number];

export const REL_TABLE_NAME = 'CodeRelation';
// FIXME  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2VERGR2R3PT06YTg1M2RhYjY=

export const REL_TYPES = [
  'CONTAINS',
  'DEFINES',
  'IMPORTS',
  'CALLS',
  'EXTENDS',
  'IMPLEMENTS',
  'HAS_METHOD',
  'HAS_PROPERTY',
  'ACCESSES',
  'METHOD_OVERRIDES',
  'OVERRIDES', // Legacy compat alias — kept until all stored indexes are migrated
  'METHOD_IMPLEMENTS',
  'MEMBER_OF',
  'STEP_IN_PROCESS',
  'HANDLES_ROUTE',
  'FETCHES',
  'HANDLES_TOOL',
  'ENTRY_POINT_OF',
  'WRAPS',
  'QUERIES',
] as const;

export type RelType = (typeof REL_TYPES)[number];
// NOTE  My80OmFIVnBZMlhva2FQbHNJL21tS1U2VERGR2R3PT06YTg1M2RhYjY=

export const EMBEDDING_TABLE_NAME = 'CodeEmbedding';
