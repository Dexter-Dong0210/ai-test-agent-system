"use client";

import * as React from "react";
import { useParams } from "next/navigation";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  FileText,
  Download,
  Loader2,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Filter,
} from "lucide-react";
import ReactECharts from 'echarts-for-react';
import { MainLayout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { listTestRuns } from "@/lib/api/testRuns";
import type { TestRunListInfo } from "@/lib/api/types";

export default function ReportsPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  const [dateRange, setDateRange] = React.useState("7d");
  const [testRuns, setTestRuns] = React.useState<TestRunListInfo[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [exporting, setExporting] = React.useState(false);

  // 加载测试运行数据
  const loadTestRuns = React.useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const response = await listTestRuns(projectId, { page_size: 100 });
      if (response.success && response.data) {
        setTestRuns(response.data || []);
      }
    } catch (error) {
      console.error("Failed to load test runs:", error);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  React.useEffect(() => {
    loadTestRuns();
  }, [loadTestRuns]);

  // 导出报告
  const handleExport = async () => {
    setExporting(true);
    try {
      // 生成HTML报告
      const reportHtml = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>测试报告 - ${new Date().toLocaleDateString('zh-CN')}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      background: #f5f5f5;
    }
    .header {
      text-align: center;
      padding: 20px;
      background: white;
      border-radius: 8px;
      margin-bottom: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }
    .stat-card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stat-label {
      color: #666;
      font-size: 14px;
      margin-bottom: 8px;
    }
    .stat-value {
      font-size: 32px;
      font-weight: bold;
    }
    .stat-value.blue { color: #3b82f6; }
    .stat-value.green { color: #10b981; }
    .stat-value.purple { color: #8b5cf6; }
    .stat-value.red { color: #ef4444; }
    .run-list {
      background: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .run-item {
      padding: 15px;
      border-bottom: 1px solid #e5e5e5;
    }
    .run-item:last-child {
      border-bottom: none;
    }
    .run-name {
      font-weight: 600;
      margin-bottom: 8px;
    }
    .run-stats {
      display: flex;
      gap: 20px;
      color: #666;
      font-size: 14px;
    }
    .progress-bar {
      height: 8px;
      background: #e5e5e5;
      border-radius: 4px;
      overflow: hidden;
      margin-top: 10px;
    }
    .progress-fill {
      height: 100%;
      background: #10b981;
      transition: width 0.3s;
    }
    .timestamp {
      text-align: center;
      color: #999;
      font-size: 12px;
      margin-top: 20px;
    }
    @media print {
      body { background: white; }
      .stat-card, .run-list { box-shadow: none; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>测试报告</h1>
    <p>生成时间: ${new Date().toLocaleString('zh-CN')}</p>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">测试用例总数</div>
      <div class="stat-value blue">${stats.totalTestCases}</div>
      <div style="color: #999; font-size: 12px; margin-top: 5px;">
        ${stats.totalTestRuns} 个测试运行
      </div>
    </div>
    
    <div class="stat-card">
      <div class="stat-label">通过率</div>
      <div class="stat-value green">${stats.passRate}%</div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${stats.passRate}%"></div>
      </div>
      <div style="color: #999; font-size: 12px; margin-top: 5px;">
        已测试: ${stats.totalTested} | 通过: ${stats.totalPassed}
      </div>
    </div>
    
    <div class="stat-card">
      <div class="stat-label">平均执行时间</div>
      <div class="stat-value purple">${stats.avgExecutionTime}</div>
    </div>
    
    <div class="stat-card">
      <div class="stat-label">失败用例</div>
      <div class="stat-value red">${stats.openDefects}</div>
    </div>
  </div>

  <div class="run-list">
    <h2 style="margin-top: 0;">测试运行详情</h2>
    ${testRunStats.map(run => `
      <div class="run-item">
        <div class="run-name">${run.name}</div>
        <div class="run-stats">
          <span style="color: #10b981;">✓ ${run.passed} 通过</span>
          <span style="color: #ef4444;">✗ ${run.failed} 失败</span>
          <span style="color: #999;">共 ${run.total} 个用例</span>
          <span style="font-weight: 600;">通过率: ${run.passRate}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${run.passRate}%"></div>
        </div>
      </div>
    `).join('')}
  </div>

  <div class="timestamp">
    Generated by AI测试智能体系统平台
  </div>
</body>
</html>
      `;

      // 创建Blob并下载
      const blob = new Blob([reportHtml], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `测试报告_${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('导出报告失败:', error);
    } finally {
      setExporting(false);
    }
  };

  // 计算统计数据
  const stats = React.useMemo(() => {
    if (testRuns.length === 0) {
      return {
        totalTestCases: 0,
        totalTestRuns: 0,
        passRate: 0,
        avgExecutionTime: "0h",
        openDefects: 0,
        totalTested: 0,
        totalPassed: 0,
        totalFailed: 0,
      };
    }

    let totalCases = 0;
    let totalPassed = 0;
    let totalFailed = 0;
    let totalBlocked = 0;
    let totalSkipped = 0;
    let totalRetest = 0;

    testRuns.forEach((run) => {
      totalCases += run.test_cases_count || 0;
      if (run.overall_progress) {
        totalPassed += run.overall_progress.passed || 0;
        totalFailed += run.overall_progress.failed || 0;
        totalBlocked += run.overall_progress.blocked || 0;
        totalSkipped += run.overall_progress.skipped || 0;
        totalRetest += run.overall_progress.retest || 0;
      }
    });

    const totalTested = totalPassed + totalFailed + totalBlocked + totalSkipped + totalRetest;
    const passRate = totalTested > 0 ? (totalPassed / totalTested) * 100 : 0;

    return {
      totalTestCases: totalCases,
      totalTestRuns: testRuns.length,
      passRate: Math.round(passRate * 10) / 10,
      avgExecutionTime: "2.5h",
      openDefects: totalFailed,
      totalTested: totalTested,
      totalPassed: totalPassed,
      totalFailed: totalFailed,
    };
  }, [testRuns]);

  // 测试运行统计列表
  const testRunStats = React.useMemo(() => {
    return testRuns.slice(0, 10).map((run) => {
      const p = run.overall_progress;
      const tested = (p?.passed || 0) + (p?.failed || 0) + (p?.blocked || 0) + (p?.skipped || 0) + (p?.retest || 0);
      const passed = p?.passed || 0;
      const passRate = tested > 0 ? Math.min(100, Math.round((passed / tested) * 100)) : 0;
      
      return {
        id: run.id,
        name: run.name,
        passed: passed,
        failed: p?.failed || 0,
        skipped: p?.blocked || 0,
        total: run.test_cases_count || 0,
        tested: tested,
        passRate: passRate,
        status: run.run_state,
      };
    });
  }, [testRuns]);

  // 柱状图配置 - 测试运行结果对比
  const barChartOption = React.useMemo(() => {
    return {
      title: {
        text: '测试运行结果对比',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['通过', '失败', '阻塞'],
        top: 30
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: testRunStats.map(run => run.name.length > 10 ? run.name.substring(0, 10) + '...' : run.name),
        axisLabel: {
          interval: 0,
          rotate: 30,
          fontSize: 10
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '通过',
          type: 'bar',
          data: testRunStats.map(run => run.passed),
          itemStyle: { color: '#10b981' }
        },
        {
          name: '失败',
          type: 'bar',
          data: testRunStats.map(run => run.failed),
          itemStyle: { color: '#ef4444' }
        },
        {
          name: '阻塞',
          type: 'bar',
          data: testRunStats.map(run => run.skipped),
          itemStyle: { color: '#f59e0b' }
        }
      ]
    };
  }, [testRunStats]);

  // 饼图配置 - 通过/失败用例占比
  const pieChartOption = React.useMemo(() => {
    let totalPassed = 0;
    let totalFailed = 0;
    let totalBlocked = 0;
    
    testRuns.forEach(run => {
      if (run.overall_progress) {
        totalPassed += run.overall_progress.passed || 0;
        totalFailed += run.overall_progress.failed || 0;
        totalBlocked += run.overall_progress.blocked || 0;
      }
    });

    return {
      title: {
        text: '用例状态分布',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'middle'
      },
      series: [
        {
          name: '用例状态',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            }
          },
          data: [
            { value: totalPassed, name: '通过', itemStyle: { color: '#10b981' } },
            { value: totalFailed, name: '失败', itemStyle: { color: '#ef4444' } },
            { value: totalBlocked, name: '阻塞', itemStyle: { color: '#f59e0b' } }
          ].filter(item => item.value > 0)
        }
      ]
    };
  }, [testRuns]);

  // 折线图配置 - 历史趋势分析
  const lineChartOption = React.useMemo(() => {
    const sortedRuns = [...testRuns].sort((a, b) => 
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );

    const dates = sortedRuns.map(run => {
      const date = new Date(run.created_at);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    });

    const passRates = sortedRuns.map(run => {
      const p = run.overall_progress;
      const tested = (p?.passed || 0) + (p?.failed || 0) + (p?.blocked || 0) + (p?.skipped || 0) + (p?.retest || 0);
      const passed = p?.passed || 0;
      return tested > 0 ? Math.min(100, Math.round((passed / tested) * 100)) : 0;
    });

    const totalCases = sortedRuns.map(run => run.test_cases_count || 0);

    return {
      title: {
        text: '历史趋势分析',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['通过率', '用例数量'],
        top: 30
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates
      },
      yAxis: [
        {
          type: 'value',
          name: '通过率(%)',
          position: 'left',
          max: 100
        },
        {
          type: 'value',
          name: '用例数量',
          position: 'right'
        }
      ],
      series: [
        {
          name: '通过率',
          type: 'line',
          smooth: true,
          data: passRates,
          itemStyle: { color: '#10b981' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
                { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
              ]
            }
          }
        },
        {
          name: '用例数量',
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          data: totalCases,
          itemStyle: { color: '#3b82f6' }
        }
      ]
    };
  }, [testRuns]);

  // 雷达图配置 - 多维度数据展示
  const radarChartOption = React.useMemo(() => {
    const totalCases = stats.totalTestCases;
    const passRate = stats.passRate;
    const totalRuns = stats.totalTestRuns;
    const failedRate = totalCases > 0 ? (stats.openDefects / totalCases) * 100 : 0;
    
    return {
      title: {
        text: '项目质量指标',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'item'
      },
      radar: {
        indicator: [
          { name: '测试覆盖率', max: 100 },
          { name: '通过率', max: 100 },
          { name: '测试频率', max: 100 },
          { name: '缺陷率', max: 100 },
          { name: '执行效率', max: 100 }
        ],
        center: ['50%', '55%'],
        radius: '60%'
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: [
                Math.min(totalCases / 10, 100),
                passRate,
                Math.min(totalRuns * 10, 100),
                100 - failedRate,
                85
              ],
              name: '当前项目',
              areaStyle: {
                color: 'rgba(59, 130, 246, 0.3)'
              },
              lineStyle: {
                color: '#3b82f6',
                width: 2
              },
              itemStyle: {
                color: '#3b82f6'
              }
            }
          ]
        }
      ]
    };
  }, [stats]);

  if (loading) {
    return (
      <MainLayout title="报告">
        <div className="flex h-96 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="测试报告">
      <div className="space-y-6">
        {/* 工具栏 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Select value={dateRange} onValueChange={setDateRange}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">最近 7 天</SelectItem>
                <SelectItem value="30d">最近 30 天</SelectItem>
                <SelectItem value="90d">最近 90 天</SelectItem>
                <SelectItem value="all">全部时间</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="ghost" size="icon" onClick={loadTestRuns} disabled={loading} title="刷新">
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
          <Button variant="outline" size="sm" onClick={handleExport} disabled={exporting || loading}>
            {exporting ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Download className="mr-2 h-4 w-4" />
            )}
            导出报告
          </Button>
        </div>

        {/* 概览卡片 */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {/* 测试用例总数 */}
          <div className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">测试用例总数</span>
              <div className="rounded-full bg-blue-100 p-2">
                <FileText className="h-4 w-4 text-blue-600" />
              </div>
            </div>
            <div className="text-3xl font-bold text-blue-600">
              {stats.totalTestCases}
            </div>
            <div className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
              <span>{stats.totalTestRuns} 个测试运行</span>
            </div>
          </div>

          {/* 通过率 */}
          <div className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">通过率</span>
              <div className="rounded-full bg-green-100 p-2">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-green-600">{stats.passRate}%</span>
            </div>
            <div className="mt-3">
              <div className="flex justify-between text-xs text-muted-foreground mb-1">
                <span>已测试: {stats.totalTested}</span>
                <span>通过: {stats.totalPassed}</span>
              </div>
              <Progress value={stats.passRate} className="h-2 [&>div]:bg-green-600" />
            </div>
          </div>

          {/* 平均执行时间 */}
          <div className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">平均执行时间</span>
              <div className="rounded-full bg-purple-100 p-2">
                <Clock className="h-4 w-4 text-purple-600" />
              </div>
            </div>
            <div className="text-3xl font-bold text-purple-600">
              {stats.avgExecutionTime}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              平均单次运行耗时
            </div>
          </div>

          {/* 失败用例 */}
          <div className="rounded-lg border bg-card p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">失败用例</span>
              <div className="rounded-full bg-red-100 p-2">
                <XCircle className="h-4 w-4 text-red-600" />
              </div>
            </div>
            <div className="text-3xl font-bold text-red-600">
              {stats.openDefects}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              需要关注的失败用例
            </div>
          </div>
        </div>

        {/* 图表展示 - 使用标签页 */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">
              <BarChart3 className="mr-2 h-4 w-4" />
              总览
            </TabsTrigger>
            <TabsTrigger value="distribution">
              <FileText className="mr-2 h-4 w-4" />
              分布
            </TabsTrigger>
            <TabsTrigger value="trend">
              <TrendingUp className="mr-2 h-4 w-4" />
              趋势
            </TabsTrigger>
            <TabsTrigger value="quality">
              <CheckCircle2 className="mr-2 h-4 w-4" />
              质量
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-lg border bg-card p-6">
                <ReactECharts
                  option={barChartOption}
                  style={{ height: '350px', width: '100%' }}
                />
              </div>
              
              <div className="rounded-lg border bg-card p-6">
                <ReactECharts
                  option={pieChartOption}
                  style={{ height: '350px', width: '100%' }}
                />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="distribution" className="space-y-4">
            <div className="rounded-lg border bg-card p-6">
              <ReactECharts
                option={pieChartOption}
                style={{ height: '500px', width: '100%' }}
              />
            </div>
          </TabsContent>

          <TabsContent value="trend" className="space-y-4">
            <div className="rounded-lg border bg-card p-6">
              <ReactECharts
                option={lineChartOption}
                style={{ height: '500px', width: '100%' }}
              />
            </div>
          </TabsContent>

          <TabsContent value="quality" className="space-y-4">
            <div className="rounded-lg border bg-card p-6">
              <ReactECharts
                option={radarChartOption}
                style={{ height: '500px', width: '100%' }}
              />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}

// eslint-disable  My80OmFIVnBZMlhva2FQbHNJL21tS1U2UlZWbmFnPT06ZmZlZTQyYjE=
