"""
ECharts MCP 集成

通过MCP协议让AI动态生成ECharts图表配置
"""
from typing import Any, Dict, List
from langchain.tools import tool
import json


class EChartsMCPGenerator:
    """ECharts MCP图表生成器"""
    
    @tool
    def generate_pie_chart(
        self,
        title: str,
        data: List[Dict[str, Any]],
        **options
    ) -> Dict:
        """
        生成饼图配置
        
        Args:
            title: 图表标题
            data: 数据列表，如 [{"name": "通过", "value": 85}, {"name": "失败", "value": 15}]
        
        Returns:
            ECharts配置对象
        """
        return {
            "title": {
                "text": title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "{a} <br/>{b}: {c} ({d}%)"
            },
            "legend": {
                "orient": "vertical",
                "left": "left"
            },
            "series": [{
                "name": title,
                "type": "pie",
                "radius": "50%",
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        }
    
    @tool
    def generate_line_chart(
        self,
        title: str,
        x_axis_data: List[str],
        series_data: List[Dict[str, Any]],
        **options
    ) -> Dict:
        """
        生成折线图配置（用于趋势分析）
        
        Args:
            title: 图表标题
            x_axis_data: X轴数据（如日期）
            series_data: 系列数据，如 [{"name": "通过率", "data": [85, 90, 88]}]
        
        Returns:
            ECharts配置对象
        """
        return {
            "title": {
                "text": title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis"
            },
            "legend": {
                "data": [s["name"] for s in series_data],
                "top": "bottom"
            },
            "xAxis": {
                "type": "category",
                "data": x_axis_data
            },
            "yAxis": {
                "type": "value"
            },
            "series": [
                {
                    "name": s["name"],
                    "type": "line",
                    "data": s["data"],
                    "smooth": True,
                    "markPoint": {
                        "data": [
                            {"type": "max", "name": "最大值"},
                            {"type": "min", "name": "最小值"}
                        ]
                    }
                }
                for s in series_data
            ]
        }
    
    @tool
    def generate_bar_chart(
        self,
        title: str,
        x_axis_data: List[str],
        series_data: List[Dict[str, Any]],
        **options
    ) -> Dict:
        """
        生成柱状图配置（用于缺陷分布、耗时分析等）
        
        Args:
            title: 图表标题
            x_axis_data: X轴数据（如模块名称）
            series_data: 系列数据
        
        Returns:
            ECharts配置对象
        """
        return {
            "title": {
                "text": title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                }
            },
            "legend": {
                "data": [s["name"] for s in series_data],
                "top": "bottom"
            },
            "xAxis": {
                "type": "category",
                "data": x_axis_data
            },
            "yAxis": {
                "type": "value"
            },
            "series": [
                {
                    "name": s["name"],
                    "type": "bar",
                    "data": s["data"],
                    "itemStyle": {
                        "color": options.get("colors", {}).get(s["name"], "#5470c6")
                    }
                }
                for s in series_data
            ]
        }
    
    @tool
    def generate_radar_chart(
        self,
        title: str,
        indicators: List[Dict[str, Any]],
        data: List[Dict[str, Any]],
        **options
    ) -> Dict:
        """
        生成雷达图（用于质量指标综合评估）
        
        Args:
            title: 图表标题
            indicators: 指标配置，如 [{"name": "覆盖率", "max": 100}]
            data: 数据，如 [{"value": [85, 90, 88], "name": "当前版本"}]
        
        Returns:
            ECharts配置对象
        """
        return {
            "title": {
                "text": title,
                "left": "center"
            },
            "tooltip": {},
            "legend": {
                "data": [d["name"] for d in data],
                "top": "bottom"
            },
            "radar": {
                "indicator": indicators
            },
            "series": [{
                "name": title,
                "type": "radar",
                "data": data
            }]
        }
    
    @tool
    def generate_gauge_chart(
        self,
        title: str,
        value: float,
        **options
    ) -> Dict:
        """
        生成仪表盘（用于显示通过率等单一指标）
        
        Args:
            title: 标题
            value: 数值（0-100）
        
        Returns:
            ECharts配置对象
        """
        return {
            "series": [{
                "type": "gauge",
                "startAngle": 200,
                "endAngle": -20,
                "min": 0,
                "max": 100,
                "splitNumber": 10,
                "itemStyle": {
                    "color": value >= 80 and "#67e0e3" or value >= 60 and "#37a2da" or "#fd666d"
                },
                "progress": {
                    "show": True,
                    "width": 30
                },
                "pointer": {
                    "show": False
                },
                "axisLine": {
                    "lineStyle": {
                        "width": 30
                    }
                },
                "axisTick": {
                    "show": False
                },
                "splitLine": {
                    "show": False
                },
                "axisLabel": {
                    "show": False
                },
                "title": {
                    "show": True,
                    "offsetCenter": [0, "70%"],
                    "fontSize": 20
                },
                "detail": {
                    "valueAnimation": True,
                    "offsetCenter": [0, "0%"],
                    "fontSize": 40,
                    "formatter": "{value}%"
                },
                "data": [{
                    "value": value,
                    "name": title
                }]
            }]
        }


# 全局实例
echarts_generator = EChartsMCPGenerator()


def get_echarts_tools():
    """获取所有ECharts MCP工具"""
    return [
        echarts_generator.generate_pie_chart,
        echarts_generator.generate_line_chart,
        echarts_generator.generate_bar_chart,
        echarts_generator.generate_radar_chart,
        echarts_generator.generate_gauge_chart,
    ]