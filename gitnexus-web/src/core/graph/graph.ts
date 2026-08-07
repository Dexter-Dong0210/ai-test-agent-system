/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2WTJOelp3PT06Yzk5ZDQ5MmM=

import type { GraphNode, GraphRelationship } from 'gitnexus-shared';
import type { KnowledgeGraph } from './types';
// NOTE  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2WTJOelp3PT06Yzk5ZDQ5MmM=

export const createKnowledgeGraph = (): KnowledgeGraph => {
  const nodeMap = new Map<string, GraphNode>();
  const relationshipMap = new Map<string, GraphRelationship>();

  const addNode = (node: GraphNode) => {
    if (!nodeMap.has(node.id)) {
      nodeMap.set(node.id, node);
    }
  };

  const addRelationship = (relationship: GraphRelationship) => {
    if (!relationshipMap.has(relationship.id)) {
      relationshipMap.set(relationship.id, relationship);
    }
  };

  return {
    get nodes() {
      return Array.from(nodeMap.values());
    },

    get relationships() {
      return Array.from(relationshipMap.values());
    },

    // O(1) count getters - avoid creating arrays just for length
    get nodeCount() {
      return nodeMap.size;
    },

    get relationshipCount() {
      return relationshipMap.size;
    },

    addNode,
    addRelationship,
  };
};
