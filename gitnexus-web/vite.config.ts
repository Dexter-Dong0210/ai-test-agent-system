/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2VDBkeVNnPT06M2VkMGZhZjc=

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  base: '/gitnexus-web/',
  plugins: [react(), tailwindcss()],
  define: {
    __REQUIRED_NODE_VERSION__: JSON.stringify('20.19.0'),
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@shared': path.resolve(__dirname, '../shared'),
      'gitnexus-shared': path.resolve(__dirname, '../gitnexus-shared/src/index.ts'),
      // Fix for Rollup failing to resolve this deep import from @langchain/anthropic
      '@anthropic-ai/sdk/lib/transform-json-schema': path.resolve(
        __dirname,
        'node_modules/@anthropic-ai/sdk/lib/transform-json-schema.mjs',
      ),
      // Fix for mermaid d3-color prototype crash on Vercel (known issue with mermaid 10.9.0+ and Vite)
      mermaid: path.resolve(__dirname, 'node_modules/mermaid/dist/mermaid.esm.min.mjs'),
    },
  },
  server: {
    // Allow serving files from node_modules
    fs: {
      allow: ['..'],
    },
  },
});
// eslint-disable  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2VDBkeVNnPT06M2VkMGZhZjc=
