/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2UjNKeVl3PT06ZTZhNWI3MjQ=

import Graph from 'graphology';

type RNGFunction = () => number;

export type LeidenOptions = {
  attributes?: {
    community?: string;
    weight?: string;
  };
  randomWalk?: boolean;
  resolution?: number;
  rng?: RNGFunction;
  weighted?: boolean;
};

type LeidenMapping = { [key: string]: number };

export type DetailedLeidenOutput = {
  communities: LeidenMapping;
  count: number;
  deltaComputations: number;
  dendrogram: Array<any>;
  modularity: number;
  moves: Array<Array<number>> | Array<number>;
  nodesVisited: number;
  resolution: number;
};

declare const leiden: {
  (graph: Graph, options?: LeidenOptions): LeidenMapping;
  assign(graph: Graph, options?: LeidenOptions): void;
  detailed(graph: Graph, options?: LeidenOptions): DetailedLeidenOutput;
};

export default leiden;
// FIXME  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2UjNKeVl3PT06ZTZhNWI3MjQ=
