#!/usr/bin/env python3
"""
YMS 相关性分析脚本

计算工艺参数与良率之间的相关性（Pearson/Spearman）
生成热力图可视化

使用方法:
    python correlation_analysis.py <数据文件.csv> [输出文件.html] [method]
    
参数:
    数据文件.csv - 输入数据文件（CSV 格式）
    输出文件.html - 输出文件名（默认：correlation_report.html）
    method - 相关方法：spearman (默认) | pearson

作者：lamber
创建日期：2026-03-21
"""

import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.offline import plot
import sys
import os

def calculate_pearson_correlation(x, y):
    """
    计算 Pearson 相关系数
    
    适用条件：
    - 连续变量
    - 正态分布
    - 线性关系
    
    参数:
        x, y: 两个连续变量数组
    
    返回:
        corr: 相关系数 (-1 到 1)
        p_value: 显著性 p 值
    """
    corr, p_value = stats.pearsonr(x, y)
    return corr, p_value

def calculate_spearman_correlation(x, y):
    """
    计算 Spearman 秩相关系数
    
    适用条件：
    - 有序变量或非正态分布
    - 单调关系
    - 对异常值更稳健（推荐用于半导体工艺数据）
    
    参数:
        x, y: 两个变量数组
    
    返回:
        corr: 相关系数 (-1 到 1)
        p_value: 显著性 p 值
    """
    corr, p_value = stats.spearmanr(x, y)
    return corr, p_value

def analyze_parameter_yield_correlation(df, param_cols, yield_col, method='spearman'):
    """
    分析多个工艺参数与良率的相关性
    
    参数:
        df: pandas DataFrame，包含工艺数据和良率数据
        param_cols: 工艺参数列名列表
        yield_col: 良率列名
        method: 'pearson' 或 'spearman'
    
    返回:
        result_df: 包含相关性分析结果的 DataFrame
    """
    results = []
    
    for param in param_cols:
        # 移除缺失值
        mask = df[[param, yield_col]].notna().all(axis=1)
        x = df.loc[mask, param]
        y = df.loc[mask, yield_col]
        
        if len(x) < 3:
            print(f"警告：参数 {param} 有效数据点不足，跳过")
            continue
        
        if method == 'pearson':
            corr, p_value = calculate_pearson_correlation(x, y)
        elif method == 'spearman':
            corr, p_value = calculate_spearman_correlation(x, y)
        else:
            raise ValueError(f"未知的方法：{method}")
        
        # 显著性标记
        if p_value < 0.001:
            significance = '***'
        elif p_value < 0.01:
            significance = '**'
        elif p_value < 0.05:
            significance = '*'
        else:
            significance = 'ns'
        
        results.append({
            'Parameter': param,
            'Correlation': corr,
            'P_value': p_value,
            'Significance': significance,
            'Abs_Correlation': abs(corr)
        })
    
    result_df = pd.DataFrame(results)
    return result_df.sort_values('Abs_Correlation', ascending=False)

def generate_correlation_matrix(df, columns=None, method='spearman'):
    """
    生成相关性矩阵
    
    参数:
        df: pandas DataFrame
        columns: 要计算相关性的列名列表（默认：所有数值列）
        method: 'pearson' 或 'spearman'
    
    返回:
        corr_matrix: 相关性矩阵 DataFrame
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    return df[columns].corr(method=method)

def plot_correlation_heatmap(corr_matrix, title='Correlation Heatmap',
                              output_file='correlation_heatmap.html'):
    """
    绘制交互式相关性热力图
    
    参数:
        corr_matrix: 相关性矩阵 DataFrame
        title: 图表标题
        output_file: 输出 HTML 文件名
    """
    z = corr_matrix.values
    x = corr_matrix.columns.tolist()
    y = corr_matrix.index.tolist()
    
    fig = go.Figure(data=go.Heatmap(
        z=z, x=x, y=y,
        colorscale='RdBu', zmid=0,
        text=np.round(z, 2),
        texttemplate='%{text}',
        colorbar=dict(title='Correlation'),
        hovertemplate='%{x} vs %{y}: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
        width=900, 
        height=700,
        margin=dict(l=100, r=50, t=80, b=100)
    )
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plot(fig, filename=output_file, auto_open=False)
    print(f"✅ 热力图已生成：{output_file}")
    return fig

def generate_correlation_report(df, param_cols, yield_col, 
                                 output_file='correlation_report.html',
                                 method='spearman'):
    """
    生成完整的相关性分析报告
    
    参数:
        df: pandas DataFrame
        param_cols: 工艺参数列名列表
        yield_col: 良率列名
        output_file: 输出 HTML 文件名
        method: 'pearson' 或 'spearman'
    
    返回:
        correlation_results: 参数与良率的相关性结果
        corr_matrix: 完整相关性矩阵
    """
    print("\n" + "="*60)
    print("YMS 相关性分析报告")
    print("="*60)
    print(f"分析方法：{method.upper()}")
    print(f"数据量：{len(df)} 条记录")
    print(f"参数数量：{len(param_cols)}")
    print(f"良率指标：{yield_col}")
    print("="*60 + "\n")
    
    # 1. 参数与良率的相关性
    print("📊 工艺参数与良率的相关性分析:")
    print("-" * 60)
    correlation_results = analyze_parameter_yield_correlation(
        df, param_cols, yield_col, method
    )
    print(correlation_results.to_string(index=False))
    
    # 识别关键影响参数（|r| >= 0.3 且 p < 0.05）
    key_params = correlation_results[
        (correlation_results['Abs_Correlation'] >= 0.3) & 
        (correlation_results['P_value'] < 0.05)
    ]
    
    if len(key_params) > 0:
        print("\n" + "="*60)
        print("🔑 关键影响参数 (|r| >= 0.3 且 p < 0.05):")
        print("="*60)
        print(key_params[['Parameter', 'Correlation', 'P_value', 'Significance']].to_string(index=False))
    else:
        print("\n⚠️  未找到显著相关的关键参数")
    
    # 2. 生成热力图
    print("\n" + "="*60)
    print("📈 生成相关性热力图...")
    all_cols = param_cols + [yield_col]
    corr_matrix = generate_correlation_matrix(df, all_cols, method)
    plot_correlation_heatmap(corr_matrix, 
                             title=f'{method.capitalize()} Correlation Heatmap',
                             output_file=output_file)
    
    print(f"\n✅ 报告生成完成：{output_file}")
    print("="*60 + "\n")
    
    return correlation_results, corr_matrix

def load_demo_data():
    """
    加载示例数据用于测试
    
    返回:
        df: 示例数据 DataFrame
    """
    np.random.seed(42)
    n_samples = 100
    
    # 生成模拟的半导体工艺数据
    df = pd.DataFrame({
        'wafer_id': range(1, n_samples + 1),
        'etch_temperature': np.random.normal(250, 5, n_samples),  # 刻蚀温度
        'deposition_pressure': np.random.normal(0.5, 0.02, n_samples),  # 沉积压力
        'implant_dose': np.random.normal(1e15, 1e13, n_samples),  # 注入剂量
        'anneal_time': np.random.normal(30, 2, n_samples),  # 退火时间
        'oxide_thickness': np.random.normal(100, 3, n_samples),  # 氧化层厚度
        'line_width': np.random.normal(0.18, 0.01, n_samples),  # 线宽
        'particle_count': np.random.poisson(5, n_samples),  # 颗粒数
        'yield_rate': np.random.normal(0.85, 0.08, n_samples)  # 良率
    })
    
    # 添加一些人为相关性
    df['yield_rate'] = (
        0.95 
        - 0.002 * df['etch_temperature'] 
        + 0.05 * df['deposition_pressure']
        - 0.001 * df['particle_count']
        + np.random.normal(0, 0.03, n_samples)
    )
    df['yield_rate'] = df['yield_rate'].clip(0, 1)
    
    return df

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == '--demo':
        print("="*60)
        print("YMS 相关性分析工具")
        print("="*60)
        print("\n用法:")
        print("  python correlation_analysis.py <数据文件.csv> [输出文件.html] [method]")
        print("  python correlation_analysis.py --demo  # 运行示例演示")
        print("\n参数:")
        print("  数据文件.csv  - 输入数据文件（CSV 格式，必须包含数值列）")
        print("  输出文件.html - 输出文件名（默认：correlation_report.html）")
        print("  method        - 相关方法：spearman (默认) | pearson")
        print("\n示例:")
        print("  python correlation_analysis.py wafer_data.csv")
        print("  python correlation_analysis.py wafer_data.csv report.html pearson")
        print("  python correlation_analysis.py --demo")
        print("\n提示:")
        print("  - 对于半导体工艺数据，推荐使用 spearman 方法（对异常值更稳健）")
        print("  - 数据文件应包含工艺参数列和良率列")
        print("  - 自动识别最后一列数值列为良率指标")
        print("="*60)
        
        # 自动运行示例
        print("\n🚀 运行示例数据演示...")
        df = load_demo_data()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        yield_col = 'yield_rate'
        param_cols = [c for c in numeric_cols if c != yield_col]
        
        generate_correlation_report(
            df, param_cols, yield_col, 
            output_file='correlation_demo_report.html',
            method='spearman'
        )
        print("\n✅ 示例演示完成！查看 correlation_demo_report.html")
        sys.exit(0)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'correlation_report.html'
    method = sys.argv[3] if len(sys.argv) > 3 else 'spearman'
    
    if not os.path.exists(input_file):
        print(f"错误：文件不存在 - {input_file}")
        sys.exit(1)
    
    print(f"读取数据文件：{input_file}")
    df = pd.read_csv(input_file)
    print(f"数据量：{len(df)} 行 × {len(df.columns)} 列")
    
    # 自动识别数值列
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        print("错误：数据文件中数值列不足 2 列")
        sys.exit(1)
    
    # 默认最后一列数值列为良率
    yield_col = numeric_cols[-1]
    param_cols = [c for c in numeric_cols if c != yield_col]
    
    print(f"工艺参数：{len(param_cols)} 列")
    print(f"良率指标：{yield_col}")
    
    generate_correlation_report(df, param_cols, yield_col, output_file, method)
