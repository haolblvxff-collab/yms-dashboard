#!/usr/bin/env python3
"""
YMS 相关性分析脚本

计算工艺参数与良率之间的相关性（Pearson/Spearman）
生成热力图可视化
"""

import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.offline import plot
import sys

def calculate_pearson_correlation(x, y):
    """
    计算 Pearson 相关系数
    
    适用条件：
    - 连续变量
    - 正态分布
    - 线性关系
    """
    corr, p_value = stats.pearsonr(x, y)
    return corr, p_value

def calculate_spearman_correlation(x, y):
    """
    计算 Spearman 秩相关系数
    
    适用条件：
    - 有序变量或非正态分布
    - 单调关系
    - 对异常值更稳健
    """
    corr, p_value = stats.spearmanr(x, y)
    return corr, p_value

def analyze_parameter_yield_correlation(df, param_cols, yield_col, method='spearman'):
    """分析多个工艺参数与良率的相关性"""
    results = []
    
    for param in param_cols:
        mask = df[[param, yield_col]].notna().all(axis=1)
        x = df.loc[mask, param]
        y = df.loc[mask, yield_col]
        
        if method == 'pearson':
            corr, p_value = calculate_pearson_correlation(x, y)
        elif method == 'spearman':
            corr, p_value = calculate_spearman_correlation(x, y)
        
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
    """生成相关性矩阵"""
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    return df[columns].corr(method=method)

def plot_correlation_heatmap(corr_matrix, title='Correlation Heatmap',
                              output_file='correlation_heatmap.html'):
    """绘制交互式相关性热力图"""
    z = corr_matrix.values
    x = corr_matrix.columns.tolist()
    y = corr_matrix.index.tolist()
    
    fig = go.Figure(data=go.Heatmap(
        z=z, x=x, y=y,
        colorscale='RdBu', zmid=0,
        text=np.round(z, 2),
        texttemplate='%{text}',
        colorbar=dict(title='Correlation')
    ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(tickangle=-45),
        width=800, height=600
    )
    
    plot(fig, filename=output_file, auto_open=False)
    print(f"热力图已生成：{output_file}")
    return fig

def generate_correlation_report(df, param_cols, yield_col, 
                                 output_file='correlation_report.html',
                                 method='spearman'):
    """生成完整的相关性分析报告"""
    print("\n=== YMS 相关性分析报告 ===\n")
    
    # 1. 参数与良率的相关性
    correlation_results = analyze_parameter_yield_correlation(
        df, param_cols, yield_col, method
    )
    print(correlation_results.to_string(index=False))
    
    # 2. 生成热力图
    all_cols = param_cols + [yield_col]
    corr_matrix = generate_correlation_matrix(df, all_cols, method)
    plot_correlation_heatmap(corr_matrix, 
                             title=f'{method.capitalize()} Correlation Heatmap',
                             output_file=output_file)
    
    print(f"\n✅ 报告生成完成：{output_file}")
    return correlation_results, corr_matrix

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python correlation_analysis.py <数据文件.csv> [输出文件.html] [method]")
        print("method: spearman (默认) | pearson")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'correlation_report.html'
    method = sys.argv[3] if len(sys.argv) > 3 else 'spearman'
    
    df = pd.read_csv(input_file)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    yield_col = numeric_cols[-1]
    param_cols = [c for c in numeric_cols if c != yield_col]
    
    generate_correlation_report(df, param_cols, yield_col, output_file, method)
