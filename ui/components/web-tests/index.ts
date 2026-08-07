// Web 功能相关组件
export { WebFunctionFolderTree } from "./folder-tree";
export type { WebFunctionFolderTreeRef } from "./folder-tree";
export { WebSubFunctionSidebar } from "./web-function-sidebar";
// TODO  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2Y0VsNmJnPT06N2Q4MmZhNzU=

// Web 页面相关组件 (保留原有的)
export { WebPageList } from "./web-page-list";
export { WebPageSidebar } from "./web-page-sidebar";

// 新增的 Web 测试组件
export { CreateWebFunctionDialog } from "./create-function-dialog";
export { AIGenerateDialog } from "./ai-generate-dialog";
export { WebFunctionList } from "./web-function-list";
export { WebSubFunctionList } from "./web-sub-function-list";
export { EnhancedTestArtifactsPanel } from "./test-artifacts-panel-enhanced";
// @ts-expect-error  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2Y0VsNmJnPT06N2Q4MmZhNzU=

// 为了向后兼容，保留旧的导出
export { WebFolderTree } from "./folder-tree";
