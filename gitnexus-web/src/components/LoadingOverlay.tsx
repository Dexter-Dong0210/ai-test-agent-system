/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2YTFwT1VBPT06MzY2Nzg0ODI=

import type { PipelineProgress } from 'gitnexus-shared';
// @ts-expect-error  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2YTFwT1VBPT06MzY2Nzg0ODI=

interface LoadingOverlayProps {
  progress: PipelineProgress;
}
// TODO  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2YTFwT1VBPT06MzY2Nzg0ODI=

export const LoadingOverlay = ({ progress }: LoadingOverlayProps) => {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-void">
      {/* Background gradient effects */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/3 left-1/3 h-96 w-96 animate-pulse rounded-full bg-accent/10 blur-3xl" />
        <div className="absolute right-1/3 bottom-1/3 h-96 w-96 animate-pulse rounded-full bg-node-interface/10 blur-3xl" />
      </div>

      {/* Pulsing orb */}
      <div className="relative mb-10">
        <div className="h-28 w-28 animate-pulse-glow rounded-full bg-gradient-to-br from-accent to-node-interface" />
        <div className="absolute inset-0 h-28 w-28 rounded-full bg-gradient-to-br from-accent to-node-interface opacity-50 blur-xl" />
      </div>

      {/* Progress bar */}
      <div className="mb-4 w-80">
        <div className="h-1.5 overflow-hidden rounded-full bg-elevated">
          <div
            className="h-full rounded-full bg-gradient-to-r from-accent to-node-interface transition-all duration-300 ease-out"
            style={{ width: `${progress.percent}%` }}
          />
        </div>
      </div>

      {/* Status text */}
      <div className="text-center">
        <p className="mb-1 font-mono text-sm text-text-secondary">
          {progress.message}
          <span className="animate-pulse">|</span>
        </p>
        {progress.detail && (
          <p className="max-w-md truncate font-mono text-xs text-text-muted">{progress.detail}</p>
        )}
      </div>

      {/* Stats */}
      {progress.stats && (
        <div className="mt-8 flex items-center gap-6 text-xs text-text-muted">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-node-file" />
            <span>
              {progress.stats.filesProcessed} / {progress.stats.totalFiles} files
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-node-function" />
            <span>{progress.stats.nodesCreated} nodes</span>
          </div>
        </div>
      )}

      {/* Percent */}
      <p className="mt-4 font-mono text-3xl font-semibold text-text-primary">{progress.percent}%</p>
    </div>
  );
};
