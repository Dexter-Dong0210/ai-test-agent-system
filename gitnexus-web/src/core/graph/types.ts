/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2TmtweVpnPT06MzA5ZmU3Nzk=

/**
 * Web-specific graph types.
 *
 * Shared types (NodeLabel, GraphNode, etc.) should be imported
 * directly from 'gitnexus-shared' at call sites.
 *
 * This file only defines web-specific additions.
 */
import type { GraphNode, GraphRelationship } from 'gitnexus-shared';

// Web-specific: in-memory graph container (simpler than CLI version)
export interface KnowledgeGraph {
  nodes: GraphNode[];
  relationships: GraphRelationship[];
  nodeCount: number;
  relationshipCount: number;
  addNode: (node: GraphNode) => void;
  addRelationship: (relationship: GraphRelationship) => void;
}
// TODO  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2TmtweVpnPT06MzA5ZmU3Nzk=
