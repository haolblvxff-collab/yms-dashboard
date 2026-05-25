#!/usr/bin/env python3
"""
YMS Wafer Map 可视化模块

实现晶圆缺陷分布图 (Wafer Map) 的交互式可视化：
- 圆形晶圆模板
- 缺陷坐标 plotting
- 按缺陷类型着色
- 图例和统计信息

使用方法:
    python wafer_map_viz.py --demo

作者：lamber
创建日期：2026-03-27
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')


class WaferMapViz:
    """Wafer Map 可视化类"""
    
    def __init__(self, wafer_diameter: float = 300.0):
        """
        初始化 Wafer Map 可视化
        
        参数:
            wafer_diameter: 晶圆直径 (mm), 默认 300mm
        """
        self.wafer_diameter = wafer_diameter
        self.wafer_radius = wafer_diameter / 2
        
        # 缺陷颜色映射
        self.defect_colors = {
            'Particle': '#FF6B6B',      # 颗粒 - 红色
            'Scratch': '#4ECDC4',       # 划伤 - 青色
            'Pit': '#FFE66D',           # 针孔 - 黄色
            'Bridge': '#95E1D3',        # 桥接 - 绿色
            'Open': '#F38181',          # 开路 - 粉色
            'Short': '#AA96DA',         # 短路 - 紫色
            'Pattern Defect': '#FCBAD3', # 图形缺陷 - 粉色
            'Other': '#A8D8EA',         # 其他 - 蓝色
        }
    
    def create_wafer_template(self) -> go.Figure:
        """
        创建晶圆模板 (圆形)
        
        返回:
            Plotly Figure 对象
        """
        # 生成圆形
        theta = np.linspace(0, 2 * np.pi, 100)
        x = self.wafer_radius * np.cos(theta)
        y = self.wafer_radius * np.sin(theta)
        
        fig = go.Figure()
        
        # 添加晶圆轮廓
        fig.add_trace(
            go.Scatter(
                x=x, y=y,
                mode='lines',
                line=dict(color='gray', width=2),
                fill='toself',
                fillcolor='rgba(240, 240, 240, 0.5)',
                name='Wafer',
                hoverinfo='skip'
            )
        )
        
        # 添加中心点
        fig.add_trace(
            go.Scatter(
                x=[0], y=[0],
                mode='markers',
                marker=dict(color='red', size=5),
                name='Center',
                hoverinfo='skip'
            )
        )
        
        # 更新布局
        fig.update_layout(
            title=f'Wafer Map Template ({self.wafer_diameter}mm)',
            xaxis=dict(
                title='X (mm)',
                scaleanchor='y',
                scaleratio=1,
                zeroline=True,
                zerolinecolor='lightgray'
            ),
            yaxis=dict(
                title='Y (mm)',
                zeroline=True,
                zerolinecolor='lightgray'
            ),
            height=600,
            width=600,
            showlegend=True,
            legend=dict(x=1, xanchor='right', y=1)
        )
        
        return fig
    
    def plot_wafer_map(self, defect_data: pd.DataFrame,
                       output_path: str = 'wafer_map.html',
                       title: str = 'Wafer Map') -> go.Figure:
        """
        绘制 Wafer Map
        
        参数:
            defect_data: 缺陷数据 DataFrame，必须包含列：
                - x: X 坐标 (mm)
                - y: Y 坐标 (mm)
                - defect_type: 缺陷类型
            output_path: 输出文件路径
            title: 图表标题
        
        返回:
            Plotly Figure 对象
        """
        # 创建基础模板
        fig = self.create_wafer_template()
        
        # 按缺陷类型分组绘图
        defect_types = defect_data['defect_type'].unique()
        
        for defect_type in defect_types:
            type_data = defect_data[defect_data['defect_type'] == defect_type]
            color = self.defect_colors.get(defect_type, '#888888')
            
            fig.add_trace(
                go.Scatter(
                    x=type_data['x'],
                    y=type_data['y'],
                    mode='markers',
                    marker=dict(
                        color=color,
                        size=8,
                        opacity=0.7,
                        line=dict(width=1, color='black')
                    ),
                    name=f'{defect_type} ({len(type_data)})',
                    text=type_data.apply(
                        lambda row: f"Type: {row['defect_type']}<br>X: {row['x']:.2f}<br>Y: {row['y']:.2f}",
                        axis=1
                    ),
                    hoverinfo='text'
                )
            )
        
        # 更新布局
        fig.update_layout(
            title=title,
            height=700,
            width=700
        )
        
        # 添加统计信息
        stats_text = self._generate_statistics(defect_data)
        fig.add_annotation(
            x=-self.wafer_radius * 0.95,
            y=-self.wafer_radius * 0.95,
            xref='x',
            yref='y',
            text=stats_text,
            showarrow=False,
            align='left',
            font=dict(size=10, family='monospace'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='gray',
            borderwidth=1,
            borderpad=4
        )
        
        # 保存图表
        fig.write_html(output_path)
        print(f"Wafer Map 已保存到：{output_path}")
        
        return fig
    
    def plot_wafer_map_by_layer(self, defect_data: pd.DataFrame,
                                 layer_column: str = 'layer',
                                 output_path: str = 'wafer_map_by_layer.html') -> go.Figure:
        """
        按工艺层绘制多个 Wafer Map
        
        参数:
            defect_data: 缺陷数据 DataFrame
            layer_column: 工艺层列名
            output_path: 输出文件路径
        
        返回:
            Plotly Figure 对象
        """
        layers = defect_data[layer_column].unique()
        n_layers = len(layers)
        
        # 计算子图布局
        n_cols = 2
        n_rows = (n_layers + 1) // 2
        
        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=[f'Layer: {layer}' for layer in layers],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # 为每个层添加 Wafer Map
        for idx, layer in enumerate(layers):
            row = idx // n_cols + 1
            col = idx % n_cols + 1
            
            layer_data = defect_data[defect_data[layer_column] == layer]
            
            # 添加晶圆轮廓
            theta = np.linspace(0, 2 * np.pi, 50)
            x = self.wafer_radius * np.cos(theta)
            y = self.wafer_radius * np.sin(theta)
            
            fig.add_trace(
                go.Scatter(
                    x=x, y=y,
                    mode='lines',
                    line=dict(color='gray', width=1),
                    fill='toself',
                    fillcolor='rgba(240, 240, 240, 0.5)',
                    showlegend=False,
                    hoverinfo='skip'
                ),
                row=row, col=col
            )
            
            # 添加缺陷点
            for defect_type in layer_data['defect_type'].unique():
                type_data = layer_data[layer_data['defect_type'] == defect_type]
                color = self.defect_colors.get(defect_type, '#888888')
                
                fig.add_trace(
                    go.Scatter(
                        x=type_data['x'],
                        y=type_data['y'],
                        mode='markers',
                        marker=dict(color=color, size=6, opacity=0.7),
                        name=f'{layer}: {defect_type}',
                        showlegend=(idx == 0),
                        hoverinfo='skip'
                    ),
                    row=row, col=col
                )
            
            # 更新子图布局
            fig.update_xaxes(
                scaleanchor='y', scaleratio=1,
                showticklabels=False,
                row=row, col=col
            )
            fig.update_yaxes(
                showticklabels=False,
                row=row, col=col
            )
        
        # 更新整体布局
        fig.update_layout(
            title='Wafer Map by Layer (按工艺层)',
            height=400 * n_rows,
            width=500 * n_cols,
            showlegend=True,
            legend=dict(x=1, xanchor='right', y=1)
        )
        
        # 保存图表
        fig.write_html(output_path)
        print(f"按层 Wafer Map 已保存到：{output_path}")
        
        return fig
    
    def _generate_statistics(self, defect_data: pd.DataFrame) -> str:
        """
        生成缺陷统计信息
        
        参数:
            defect_data: 缺陷数据 DataFrame
        
        返回:
            统计信息字符串
        """
        total_defects = len(defect_data)
        defect_density = total_defects / (np.pi * self.wafer_radius ** 2)
        
        stats = [
            f"Total Defects: {total_defects}",
            f"Density: {defect_density:.4f} defects/mm²",
            "",
            "By Type:"
        ]
        
        # 按类型统计
        type_counts = defect_data['defect_type'].value_counts()
        for defect_type, count in type_counts.items():
            percentage = count / total_defects * 100
            stats.append(f"  {defect_type}: {count} ({percentage:.1f}%)")
        
        return '\n'.join(stats)
    
    def run_demo(self):
        """运行示例演示"""
        print("=" * 60)
        print("Wafer Map Visualization Demo (Wafer Map 可视化演示)")
        print("=" * 60)
        
        # 生成模拟缺陷数据
        np.random.seed(42)
        n_defects = 200
        
        # 生成随机坐标 (在晶圆内)
        theta = np.random.uniform(0, 2 * np.pi, n_defects)
        r = np.sqrt(np.random.uniform(0, 1, n_defects)) * self.wafer_radius
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # 生成缺陷类型
        defect_types = np.random.choice(
            ['Particle', 'Scratch', 'Pit', 'Bridge', 'Open'],
            size=n_defects,
            p=[0.4, 0.2, 0.2, 0.1, 0.1]
        )
        
        # 生成工艺层
        layers = np.random.choice(['M1', 'M2', 'M3', 'POLY'], size=n_defects)
        
        # 创建 DataFrame
        defect_data = pd.DataFrame({
            'x': x,
            'y': y,
            'defect_type': defect_types,
            'layer': layers
        })
        
        print("\n1. 生成基础 Wafer Map...")
        self.plot_wafer_map(
            defect_data,
            output_path='wafer_map_demo.html',
            title='Wafer Map Demo (300mm)'
        )
        
        print("\n2. 生成按层 Wafer Map...")
        self.plot_wafer_map_by_layer(
            defect_data,
            output_path='wafer_map_by_layer.html'
        )
        
        # 生成边缘缺陷数据
        print("\n3. 生成边缘缺陷 Wafer Map...")
        edge_theta = np.random.uniform(0, 2 * np.pi, 100)
        edge_r = np.random.uniform(0.8, 1.0, 100) * self.wafer_radius
        edge_x = edge_r * np.cos(edge_theta)
        edge_y = edge_r * np.sin(edge_theta)
        edge_defects = pd.DataFrame({
            'x': edge_x,
            'y': edge_y,
            'defect_type': np.random.choice(['Particle', 'Scratch'], size=100)
        })
        
        self.plot_wafer_map(
            edge_defects,
            output_path='wafer_map_edge_defects.html',
            title='Edge Defects (边缘缺陷)'
        )
        
        # 生成中心缺陷数据
        print("\n4. 生成中心缺陷 Wafer Map...")
        center_theta = np.random.uniform(0, 2 * np.pi, 80)
        center_r = np.random.uniform(0, 0.3, 80) * self.wafer_radius
        center_x = center_r * np.cos(center_theta)
        center_y = center_r * np.sin(center_theta)
        center_defects = pd.DataFrame({
            'x': center_x,
            'y': center_y,
            'defect_type': np.random.choice(['Pit', 'Bridge'], size=80)
        })
        
        self.plot_wafer_map(
            center_defects,
            output_path='wafer_map_center_defects.html',
            title='Center Defects (中心缺陷)'
        )
        
        print("\n" + "=" * 60)
        print("Demo 完成！请查看生成的 HTML 文件。")
        print("=" * 60)


if __name__ == '__main__':
    viz = WaferMapViz()
    viz.run_demo()
