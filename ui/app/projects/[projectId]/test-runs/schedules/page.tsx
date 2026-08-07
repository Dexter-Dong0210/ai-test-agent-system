"use client";
// FIXME  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2VEhneFNRPT06ZTY0NDQ0NDA=

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Plus,
  ArrowLeft,
  CalendarClock,
  Clock,
  Play,
  Loader2,
  AlertCircle,
  RefreshCw,
  Pencil,
  Trash2,
  MoreHorizontal,
  CheckCircle2,
  XCircle,
  Search,
  Code,
  Layers,
  Globe,
  CheckSquare,
  Square,
  Filter,
} from "lucide-react";
import { MainLayout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Pagination,
} from "@/components/ui/pagination";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent } from "@/components/ui/card";
import {
  getSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  type TestRunScheduleInfo,
  type TestRunScheduleCreate,
  type ScheduleTriggerType,
  type ScriptType,
} from "@/lib/api";
import { ApiError } from "@/lib/api/client";
import { listAPITests } from "@/lib/api/api-tests";
import type { APITest } from "@/lib/api/api-tests";
import { listWebTests } from "@/lib/api/web-tests";
import type { WebTest } from "@/lib/api/web-tests";
import { listScenarios } from "@/lib/api/scenarios";
import type { Scenario } from "@/types/scenario";
// @ts-expect-error  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2VEhneFNRPT06ZTY0NDQ0NDA=

const PAGE_SIZE = 20;

const TRIGGER_TYPE_LABEL: Record<ScheduleTriggerType, string> = {
  cron: "Cron 表达式",
  interval: "间隔触发",
  date: "一次性",
};
// @ts-expect-error  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2VEhneFNRPT06ZTY0NDQ0NDA=

function formatNextRun(dateStr?: string): string {
  if (!dateStr) return "未计算";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return "无效时间";
  return d.toLocaleString();
}

function buildCronDescription(config: Record<string, unknown>): string {
  if (config.cron_expression) {
    return String(config.cron_expression);
  }
  if (config.minutes !== undefined) {
    return `每 ${config.minutes} 分钟`;
  }
  if (config.hours !== undefined) {
    return `每 ${config.hours} 小时`;
  }
  if (config.days !== undefined) {
    return `每 ${config.days} 天`;
  }
  return JSON.stringify(config);
}

export default function SchedulesPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;

  const [items, setItems] = React.useState<TestRunScheduleInfo[]>([]);
  const [total, setTotal] = React.useState(0);
  const [page, setPage] = React.useState(1);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const [createOpen, setCreateOpen] = React.useState(false);
  const [createForm, setCreateForm] = React.useState<TestRunScheduleCreate>({
    name: "",
    description: "",
    trigger_type: "cron",
    trigger_config: { cron_expression: "0 9 * * *" },
    test_run_template: { 
      name: "定时执行", 
      execution_mode: "sequential",
      scripts: [] 
    },
    is_enabled: true,
  });
  const [creating, setCreating] = React.useState(false);

  // 脚本选择器状态
  const [scriptTab, setScriptTab] = React.useState<ScriptType | "all">("all");
  const [apiTests, setApiTests] = React.useState<APITest[]>([]);
  const [scenarios, setScenarios] = React.useState<Scenario[]>([]);
  const [webTests, setWebTests] = React.useState<WebTest[]>([]);
  const [scriptSearch, setScriptSearch] = React.useState("");
  const [scriptsLoading, setScriptsLoading] = React.useState(false);

  const [editingSchedule, setEditingSchedule] = React.useState<TestRunScheduleInfo | null>(null);
  const [editForm, setEditForm] = React.useState<Partial<TestRunScheduleCreate>>({});
  const [editSaving, setEditSaving] = React.useState(false);

  const [deletingSchedule, setDeletingSchedule] = React.useState<TestRunScheduleInfo | null>(null);
  const [deleting, setDeleting] = React.useState(false);

  const loadList = React.useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await getSchedules(projectId, { page, page_size: PAGE_SIZE });
      setItems(response.data.items);
      setTotal(response.data.total);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "加载调度列表失败";
      setError(msg);
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [projectId, page]);

  React.useEffect(() => {
    loadList();
  }, [loadList]);

  // 加载所有脚本列表（并行加载三种类型）
  const loadScripts = React.useCallback(async () => {
    if (!projectId || !createOpen) return;
    setScriptsLoading(true);
    try {
      const [apiRes, scenarioRes, webRes] = await Promise.allSettled([
        listAPITests(projectId, { page: 1, page_size: 300 }),
        listScenarios(projectId, { page: 1, page_size: 300 }),
        listWebTests(projectId, { page: 1, page_size: 300 }),
      ]);

      if (apiRes.status === "fulfilled") {
        setApiTests(apiRes.value.items || []);
      }
      if (scenarioRes.status === "fulfilled") {
        setScenarios(scenarioRes.value.items || []);
      }
      if (webRes.status === "fulfilled") {
        setWebTests(webRes.value.items || []);
      }
    } catch (err) {
      console.error("[Schedule] loadScripts error:", err);
    } finally {
      setScriptsLoading(false);
    }
  }, [projectId, createOpen]);

  React.useEffect(() => {
    loadScripts();
  }, [loadScripts]);

  function resetCreateForm() {
    setCreateForm({
      name: "",
      description: "",
      trigger_type: "cron",
      trigger_config: { cron_expression: "0 9 * * *" },
      test_run_template: { 
        name: "定时执行", 
        execution_mode: "sequential",
        scripts: [] 
      },
      is_enabled: true,
    });
    setScriptSearch("");
    setScriptTab("all");
  }

  // ========== 脚本选择器辅助逻辑 ==========

  interface UnifiedScript {
    id: string;
    type: ScriptType;
    identifier: string;
    name: string;
    description?: string;
    typeLabel: string;
    typeIcon: React.ReactNode;
    meta: { label: string; value: string }[];
    createdAt: string;
  }

  const allScriptItems = React.useMemo<UnifiedScript[]>(() => {
    const items: UnifiedScript[] = [];

    apiTests.forEach((t) => {
      items.push({
        id: t.id,
        type: "api_test",
        identifier: t.identifier,
        name: t.name,
        description: t.description ?? undefined,
        typeLabel: "API 测试",
        typeIcon: <Code className="h-3.5 w-3.5" />,
        meta: [
          { label: "端点", value: String(t.total_endpoints ?? 0) },
          { label: "场景", value: String(t.total_scenarios ?? 0) },
          { label: "格式", value: t.script_format || "playwright" },
        ],
        createdAt: t.created_at,
      });
    });

    scenarios.forEach((s) => {
      items.push({
        id: s.id,
        type: "scenario",
        identifier: s.identifier,
        name: s.name,
        description: s.description ?? undefined,
        typeLabel: "场景测试",
        typeIcon: <Layers className="h-3.5 w-3.5" />,
        meta: [
          { label: "步骤", value: String(s.total_steps ?? 0) },
          ...(s.last_run_status ? [{ label: "上次", value: s.last_run_status }] : []),
        ],
        createdAt: s.created_at,
      });
    });

    webTests.forEach((t) => {
      items.push({
        id: t.id,
        type: "web_test",
        identifier: t.identifier,
        name: t.name,
        description: t.description ?? undefined,
        typeLabel: "Web 测试",
        typeIcon: <Globe className="h-3.5 w-3.5" />,
        meta: [
          { label: "页面", value: String(t.total_pages ?? 0) },
          { label: "流程", value: String(t.total_flows ?? 0) },
          { label: "格式", value: t.script_format || "playwright" },
        ],
        createdAt: t.created_at,
      });
    });

    return items;
  }, [apiTests, scenarios, webTests]);

  const filteredScripts = React.useMemo(() => {
    let result = allScriptItems;

    if (scriptTab !== "all") {
      result = result.filter((s) => s.type === scriptTab);
    }

    if (scriptSearch.trim()) {
      const q = scriptSearch.trim().toLowerCase();
      result = result.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.identifier.toLowerCase().includes(q)
      );
    }

    return result;
  }, [allScriptItems, scriptTab, scriptSearch]);

  const isScriptSelected = (type: ScriptType, id: string) => {
    return (
      createForm.test_run_template.scripts?.some(
        (s) => s.script_type === type && s.script_id === id
      ) ?? false
    );
  };

  const toggleScriptSelection = (script: UnifiedScript) => {
    const scripts = createForm.test_run_template.scripts ?? [];
    const exists = scripts.some(
      (s) => s.script_type === script.type && s.script_id === script.id
    );

    if (exists) {
      setCreateForm({
        ...createForm,
        test_run_template: {
          ...createForm.test_run_template,
          scripts: scripts.filter(
            (s) => !(s.script_type === script.type && s.script_id === script.id)
          ),
        },
      });
    } else {
      setCreateForm({
        ...createForm,
        test_run_template: {
          ...createForm.test_run_template,
          scripts: [
            ...scripts,
            {
              script_type: script.type,
              script_id: script.id,
              script_identifier: script.identifier,
              script_name: script.name,
            },
          ],
        },
      });
    }
  };

  const selectedCountByType = React.useMemo(() => {
    const counts: Record<string, number> = {};
    createForm.test_run_template.scripts?.forEach((s) => {
      counts[s.script_type] = (counts[s.script_type] || 0) + 1;
    });
    return counts;
  }, [createForm.test_run_template.scripts]);

  async function handleCreate() {
    if (!createForm.name.trim()) return;
    setCreating(true);
    try {
      await createSchedule(projectId, {
        ...createForm,
        name: createForm.name.trim(),
        description: createForm.description?.trim() || undefined,
      });
      setCreateOpen(false);
      resetCreateForm();
      setPage(1);
      await loadList();
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "创建调度失败";
      setError(msg);
    } finally {
      setCreating(false);
    }
  }

  function openEdit(schedule: TestRunScheduleInfo) {
    setEditingSchedule(schedule);
    setEditForm({
      name: schedule.name,
      description: schedule.description,
      trigger_type: schedule.trigger_type,
      trigger_config: schedule.trigger_config,
      test_run_template: schedule.test_run_template || { name: "定时执行" },
      is_enabled: schedule.is_enabled,
    });
  }

  async function handleEditSave() {
    if (!editingSchedule) return;
    setEditSaving(true);
    try {
      await updateSchedule(projectId, editingSchedule.id, editForm);
      setEditingSchedule(null);
      await loadList();
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "更新调度失败";
      setError(msg);
    } finally {
      setEditSaving(false);
    }
  }

  async function handleDelete() {
    if (!deletingSchedule) return;
    setDeleting(true);
    try {
      await deleteSchedule(projectId, deletingSchedule.id);
      setDeletingSchedule(null);
      await loadList();
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "删除调度失败";
      setError(msg);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <MainLayout title="定时调度">
      <div className="space-y-6">
        {/* 导航 */}
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => router.push(`/projects/${projectId}/test-runs`)}>
            <ArrowLeft className="mr-1 h-4 w-4" />
            返回测试运行
          </Button>
        </div>

        {/* 工具栏 */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={loadList} disabled={loading} title="刷新">
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            新建调度
          </Button>
        </div>

        {error && (
          <div className="flex items-center gap-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </div>
        )}

        {/* 列表 */}
        <div className="rounded-lg border bg-card">
          {loading ? (
            <div className="flex h-64 items-center justify-center">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : items.length === 0 ? (
            <div className="flex h-64 flex-col items-center justify-center gap-2">
              <CalendarClock className="h-12 w-12 text-muted-foreground/50" />
              <p className="text-muted-foreground">暂无定时调度</p>
            </div>
          ) : (
            <div className="divide-y">
              {items.map((schedule) => (
                <div
                  key={schedule.id}
                  className="flex items-center justify-between p-4 hover:bg-muted/50"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <CalendarClock className="h-5 w-5 text-primary" />
                      <h3 className="font-medium truncate">{schedule.name}</h3>
                      <Badge variant={schedule.is_enabled ? "default" : "secondary"}>
                        {schedule.is_enabled ? (
                          <>
                            <CheckCircle2 className="mr-1 h-3 w-3" />
                            启用
                          </>
                        ) : (
                          <>
                            <XCircle className="mr-1 h-3 w-3" />
                            禁用
                          </>
                        )}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {TRIGGER_TYPE_LABEL[schedule.trigger_type]}
                      </Badge>
                    </div>
                    <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5" />
                        {buildCronDescription(schedule.trigger_config)}
                      </span>
                      <span>下次执行: {formatNextRun(schedule.next_run_at)}</span>
                      {schedule.last_run_at && (
                        <span>上次执行: {new Date(schedule.last_run_at).toLocaleString()}</span>
                      )}
                    </div>
                  </div>
                  <div className="ml-4 flex items-center gap-2">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => openEdit(schedule)}>
                          <Pencil className="mr-2 h-4 w-4" />
                          编辑
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => setDeletingSchedule(schedule)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          删除
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 分页 */}
        {total > 0 && (
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            total={total}
            onPageChange={setPage}
            showPageSizeSelector={false}
          />
        )}
      </div>

      {/* 创建对话框 */}
      <Dialog
        open={createOpen}
        onOpenChange={(open) => {
          setCreateOpen(open);
          if (!open) resetCreateForm();
        }}
      >
        <DialogContent className="max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>新建定时调度</DialogTitle>
            <DialogDescription>
              创建定时调度以自动执行测试运行。
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-y-auto pr-2 -mx-2">
            <div className="space-y-4 py-4 px-2">
            <div className="space-y-2">
              <Label htmlFor="sch-name">名称 *</Label>
              <Input
                id="sch-name"
                value={createForm.name}
                onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                placeholder="例如: 每日回归测试"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sch-desc">描述</Label>
              <Textarea
                id="sch-desc"
                value={(createForm.description as string) ?? ""}
                onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                placeholder="可选描述"
                rows={2}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sch-exec-mode">执行模式</Label>
              <Select
                value={createForm.test_run_template.execution_mode ?? "sequential"}
                onValueChange={(v) =>
                  setCreateForm({
                    ...createForm,
                    test_run_template: {
                      ...createForm.test_run_template,
                      execution_mode: v as "sequential" | "parallel",
                    },
                  })
                }
              >
                <SelectTrigger id="sch-exec-mode">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sequential">顺序执行</SelectItem>
                  <SelectItem value="parallel">并行执行</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {createForm.test_run_template.execution_mode === "parallel" && (
              <div className="space-y-2">
                <Label htmlFor="sch-concurrency">最大并发数</Label>
                <Input
                  id="sch-concurrency"
                  type="number"
                  min={1}
                  max={20}
                  value={createForm.test_run_template.max_concurrency ?? 5}
                  onChange={(e) =>
                    setCreateForm({
                      ...createForm,
                      test_run_template: {
                        ...createForm.test_run_template,
                        max_concurrency: parseInt(e.target.value) || 5,
                      },
                    })
                  }
                />
              </div>
            )}
            
            {/* 脚本选择器 */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-base font-medium">选择执行脚本</Label>
                <div className="flex items-center gap-3 text-sm">
                  {selectedCountByType["api_test"] ? (
                    <span className="flex items-center gap-1 text-blue-600">
                      <Code className="h-3.5 w-3.5" />
                      API {selectedCountByType["api_test"]}
                    </span>
                  ) : null}
                  {selectedCountByType["scenario"] ? (
                    <span className="flex items-center gap-1 text-amber-600">
                      <Layers className="h-3.5 w-3.5" />
                      场景 {selectedCountByType["scenario"]}
                    </span>
                  ) : null}
                  {selectedCountByType["web_test"] ? (
                    <span className="flex items-center gap-1 text-green-600">
                      <Globe className="h-3.5 w-3.5" />
                      Web {selectedCountByType["web_test"]}
                    </span>
                  ) : null}
                  {!createForm.test_run_template.scripts?.length ? (
                    <span className="text-muted-foreground">未选择脚本</span>
                  ) : (
                    <span className="font-medium">
                      共 {createForm.test_run_template.scripts.length} 个
                    </span>
                  )}
                </div>
              </div>

              {/* 工具栏 */}
              <div className="flex flex-wrap items-center gap-2">
                <Tabs
                  value={scriptTab}
                  onValueChange={(v) => setScriptTab(v as ScriptType | "all")}
                >
                  <TabsList>
                    <TabsTrigger value="all">
                      全部
                      {allScriptItems.length > 0 && (
                        <span className="ml-1 text-xs text-muted-foreground">
                          ({allScriptItems.length})
                        </span>
                      )}
                    </TabsTrigger>
                    <TabsTrigger value="api_test">
                      <Code className="mr-1 h-3.5 w-3.5" />
                      API
                    </TabsTrigger>
                    <TabsTrigger value="scenario">
                      <Layers className="mr-1 h-3.5 w-3.5" />
                      场景
                    </TabsTrigger>
                    <TabsTrigger value="web_test">
                      <Globe className="mr-1 h-3.5 w-3.5" />
                      Web
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
                <div className="relative flex-1 min-w-[180px]">
                  <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="搜索标识符或名称..."
                    value={scriptSearch}
                    onChange={(e) => setScriptSearch(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const visible = filteredScripts;
                    const newSelections = visible
                      .filter((item) => !isScriptSelected(item.type, item.id))
                      .map((item) => ({
                        script_type: item.type,
                        script_id: item.id,
                        script_identifier: item.identifier,
                        script_name: item.name,
                      }));
                    setCreateForm({
                      ...createForm,
                      test_run_template: {
                        ...createForm.test_run_template,
                        scripts: [
                          ...(createForm.test_run_template.scripts ?? []),
                          ...newSelections,
                        ],
                      },
                    });
                  }}
                >
                  <CheckSquare className="mr-1 h-3.5 w-3.5" />
                  全选
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const visibleIds = new Set(filteredScripts.map((i) => i.id));
                    setCreateForm({
                      ...createForm,
                      test_run_template: {
                        ...createForm.test_run_template,
                        scripts: (createForm.test_run_template.scripts ?? []).filter(
                          (s) => !visibleIds.has(s.script_id)
                        ),
                      },
                    });
                  }}
                >
                  <Square className="mr-1 h-3.5 w-3.5" />
                  取消全选
                </Button>
              </div>

              {/* 脚本表格 */}
              <Card>
                <CardContent className="p-0">
                  <ScrollArea className="h-[200px]">
                    <div className="sticky top-0 z-10 grid grid-cols-[44px_1.2fr_0.8fr_1fr_90px] gap-2 border-b bg-muted/60 px-3 py-2 text-xs font-medium text-muted-foreground backdrop-blur-sm">
                      <div>选择</div>
                      <div>标识符 / 名称</div>
                      <div>类型</div>
                      <div>元数据</div>
                      <div>创建时间</div>
                    </div>

                    {scriptsLoading ? (
                      <div className="flex h-40 items-center justify-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        加载脚本中...
                      </div>
                    ) : filteredScripts.length === 0 ? (
                      <div className="flex h-40 flex-col items-center justify-center gap-2 text-sm text-muted-foreground">
                        <Filter className="h-8 w-8 opacity-40" />
                        <span>
                          {allScriptItems.length === 0
                            ? "暂无可用脚本，请先创建 API 测试、场景或 Web 测试"
                            : "没有匹配当前筛选条件的脚本"}
                        </span>
                      </div>
                    ) : (
                      filteredScripts.map((item) => {
                        const selected = isScriptSelected(item.type, item.id);
                        return (
                          <div
                            key={`${item.type}-${item.id}`}
                            className="grid grid-cols-[44px_1.2fr_0.8fr_1fr_90px] gap-2 border-b px-3 py-2.5 text-sm items-center transition-colors hover:bg-muted/40 last:border-b-0"
                          >
                            <Checkbox
                              checked={selected}
                              onCheckedChange={() => toggleScriptSelection(item)}
                            />
                            <div className="min-w-0">
                              <div className="truncate font-medium">
                                {item.name}
                              </div>
                              <div className="truncate text-xs text-muted-foreground font-mono">
                                {item.identifier}
                              </div>
                              {item.description && (
                                <div className="truncate text-xs text-muted-foreground mt-0.5">
                                  {item.description}
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-1.5">
                              <span className="text-muted-foreground">
                                {item.typeIcon}
                              </span>
                              <Badge
                                variant="outline"
                                className="text-xs font-normal"
                              >
                                {item.typeLabel}
                              </Badge>
                            </div>
                            <div className="flex flex-wrap gap-x-2 gap-y-0.5 text-xs text-muted-foreground">
                              {item.meta.map((m) => (
                                <span key={m.label}>
                                  <span className="text-muted-foreground/60">
                                    {m.label}
                                  </span>{" "}
                                  {m.value}
                                </span>
                              ))}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {new Date(item.createdAt).toLocaleDateString("zh-CN")}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>

              {/* 已选脚本摘要 */}
              {createForm.test_run_template.scripts && createForm.test_run_template.scripts.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {createForm.test_run_template.scripts.map((s, idx) => (
                    <Badge
                      key={idx}
                      variant="secondary"
                      className="text-xs gap-1 pr-1"
                    >
                      {s.script_name || s.script_identifier || s.script_id}
                      <button
                        className="ml-0.5 rounded-full hover:bg-destructive/20 hover:text-destructive transition-colors"
                        onClick={() => {
                          setCreateForm({
                            ...createForm,
                            test_run_template: {
                              ...createForm.test_run_template,
                              scripts: (createForm.test_run_template.scripts ?? []).filter(
                                (_, i) => i !== idx
                              ),
                            },
                          });
                        }}
                      >
                        <XCircle className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>
            <div className="space-y-2">
              <Label>触发器类型</Label>
              <Select
                value={createForm.trigger_type}
                onValueChange={(v) => {
                  const type = v as ScheduleTriggerType;
                  let config: Record<string, unknown> = {};
                  if (type === "cron") config = { cron_expression: "0 9 * * *" };
                  else if (type === "interval") config = { minutes: 60 };
                  else if (type === "date") config = { run_date: new Date().toISOString() };
                  setCreateForm({ ...createForm, trigger_type: type, trigger_config: config });
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cron">Cron 表达式</SelectItem>
                  <SelectItem value="interval">间隔触发</SelectItem>
                  <SelectItem value="date">一次性</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {createForm.trigger_type === "cron" && (
              <div className="space-y-2">
                <Label htmlFor="sch-cron">Cron 表达式</Label>
                <Input
                  id="sch-cron"
                  value={String(createForm.trigger_config.cron_expression || "")}
                  onChange={(e) =>
                    setCreateForm({
                      ...createForm,
                      trigger_config: { cron_expression: e.target.value },
                    })
                  }
                  placeholder="0 9 * * *"
                />
                <p className="text-xs text-muted-foreground">格式: 分 时 日 月 周</p>
              </div>
            )}
            {createForm.trigger_type === "interval" && (
              <div className="space-y-2">
                <Label htmlFor="sch-interval">间隔分钟数</Label>
                <Input
                  id="sch-interval"
                  type="number"
                  value={Number(createForm.trigger_config.minutes || 60)}
                  onChange={(e) =>
                    setCreateForm({
                      ...createForm,
                      trigger_config: { minutes: Number(e.target.value) },
                    })
                  }
                />
              </div>
            )}
            {createForm.trigger_type === "date" && (
              <div className="space-y-2">
                <Label htmlFor="sch-date">执行时间</Label>
                <Input
                  id="sch-date"
                  type="datetime-local"
                  value={String(createForm.trigger_config.run_date || "").slice(0, 16)}
                  onChange={(e) =>
                    setCreateForm({
                      ...createForm,
                      trigger_config: { run_date: new Date(e.target.value).toISOString() },
                    })
                  }
                />
              </div>
            )}
            <div className="flex items-center gap-2">
              <Checkbox
                id="sch-enabled"
                checked={createForm.is_enabled}
                onCheckedChange={(checked) => setCreateForm({ ...createForm, is_enabled: checked === true })}
              />
              <Label htmlFor="sch-enabled">立即启用</Label>
            </div>
          </div>
        </div>
        <DialogFooter className="border-t pt-4">
            <Button variant="outline" onClick={() => setCreateOpen(false)} disabled={creating}>
              取消
            </Button>
            <Button onClick={handleCreate} disabled={creating || !createForm.name.trim()}>
              {creating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              创建
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑对话框 */}
      <Dialog open={editingSchedule !== null} onOpenChange={(open) => !open && setEditingSchedule(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>编辑调度</DialogTitle>
            <DialogDescription>
              {editingSchedule ? `修改 ${editingSchedule.name}` : ""}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>名称</Label>
              <Input
                value={editForm.name || ""}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>描述</Label>
              <Textarea
                value={(editForm.description as string) || ""}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                rows={2}
              />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="edit-enabled"
                checked={editForm.is_enabled}
                onCheckedChange={(checked) => setEditForm({ ...editForm, is_enabled: checked === true })}
              />
              <Label htmlFor="edit-enabled">启用</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingSchedule(null)} disabled={editSaving}>
              取消
            </Button>
            <Button onClick={handleEditSave} disabled={editSaving || !editForm.name?.trim()}>
              {editSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认 */}
      <AlertDialog
        open={deletingSchedule !== null}
        onOpenChange={(open) => !open && setDeletingSchedule(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>删除调度?</AlertDialogTitle>
            <AlertDialogDescription>
              确认删除 {deletingSchedule?.name}？此操作不可恢复。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </MainLayout>
  );
}
// FIXME  My80OmFIVnBZMlhva2FQbHNJL21tS1U2VEhneFNRPT06ZTY0NDQ0NDA=
