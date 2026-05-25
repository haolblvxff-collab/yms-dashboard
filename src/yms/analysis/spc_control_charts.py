#!/usr/bin/env python3
"""
YMS SPC 控制图模块

实现统计过程控制 (SPC) 的各种控制图：
- X-bar R 图 (均值 - 极差图)
- I-MR 图 (单值 - 移动极差图)
- P-Chart (不合格品率图)
- C-Chart (缺陷数图)
- U-Chart (单位缺陷数图)

支持 Western Electric Rules (6 条判异规则)

使用方法:
    python spc_control_charts.py --demo

作者：lamber
创建日期：2026-03-30
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Tuple, Dict, Optional
import warnings

warnings.filterwarnings('ignore')


class SPCControlCharts:
    """SPC 控制图类"""
    
    def __init__(self):
        """初始化 SPC 控制图"""
        self.western_electric_rules = {
            'rule1': '单点超出±3σ',
            'rule2': '连续 9 点同侧',
            'rule3': '连续 6 点上升/下降',
            'rule4': '连续 14 点交替',
            'rule5': '连续 3 点中 2 点超出±2σ',
            'rule6': '连续 5 点中 4 点超出±1σ',
        }
    
    def calculate_control_limits(self, data: np.ndarray) -> Dict:
        """
        计算控制限
        
        参数:
            data: 数据数组
        
        返回:
            包含 UCL, CL, LCL 的字典
        """
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        return {
            'UCL': mean + 3 * std,  # 上控制限
            'CL': mean,              # 中心线
            'LCL': mean - 3 * std,  # 下控制限
            'mean': mean,
            'std': std,
        }
    
    def plot_xbar_r(self, data: pd.DataFrame, 
                    subgroup_size: int = 5,
                    output_path: str = 'xbar_r_chart.html') -> go.Figure:
        """
        绘制 X-bar R 图 (均值 - 极差图)
        
        适用场景：计量型数据，子组样本
        
        参数:
            data: 数据 DataFrame，每行一个子组
            subgroup_size: 子组大小
            output_path: 输出文件路径
        
        返回:
            Plotly Figure 对象
        """
        # 计算每个子组的均值和极差
        xbar = data.mean(axis=1)
        R = data.max(axis=1) - data.min(axis=1)
        
        # 计算控制限
        xbar_limits = self.calculate_control_limits(xbar)
        R_limits = self.calculate_control_limits(R)
        
        # 创建子图
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=('X-bar Chart (均值图)', 'R Chart (极差图)'),
                           vertical_spacing=0.1)
        
        # X-bar 图
        fig.add_trace(
            go.Scatter(y=xbar, mode='lines+markers', name='X-bar', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_hline(y=xbar_limits['UCL'], line_dash="dash", line_color="red", name='UCL', row=1, col=1)
        fig.add_hline(y=xbar_limits['CL'], line_dash="solid", line_color="green", name='CL', row=1, col=1)
        fig.add_hline(y=xbar_limits['LCL'], line_dash="dash", line_color="red", name='LCL', row=1, col=1)
        
        # R 图
        fig.add_trace(
            go.Scatter(y=R, mode='lines+markers', name='R', line=dict(color='blue')),
            row=2, col=1
        )
        fig.add_hline(y=R_limits['UCL'], line_dash="dash", line_color="red", name='UCL', row=2, col=1)
        fig.add_hline(y=R_limits['CL'], line_dash="solid", line_color="green", name='CL', row=2, col=1)
        fig.add_hline(y=R_limits['LCL'], line_dash="dash", line_color="red", name='LCL', row=2, col=1)
        
        # 更新布局
        fig.update_layout(
            title='X-bar R Control Chart (均值 - 极差控制图)',
            height=800,
            showlegend=True,
            legend=dict(x=1, xanchor='right', y=1)
        )
        
        # 保存图表
        fig.write_html(output_path)
        print(f"X-bar R 图已保存到：{output_path}")
        
        return fig
    
    def plot_imr(self, data: np.ndarray, 
                 output_path: str = 'imr_chart.html') -> go.Figure:
        """
        绘制 I-MR 图 (单值 - 移动极差图)
        
        适用场景：计量型数据，单个样本
        
        参数:
            data: 数据数组
            output_path: 输出文件路径
        
        返回:
            Plotly Figure 对象
        """
        # 计算移动极差
        mr = np.abs(np.diff(data))
        mr = np.insert(mr, 0, np.nan)  # 第一个值为 NaN
        
        # 计算控制限
        I_limits = self.calculate_control_limits(data)
        MR_limits = self.calculate_control_limits(mr[1:])  # 排除 NaN
        
        # 创建子图
        fig = make_subplots(rows=2, cols=1,
                           subplot_titles=('I Chart (单值图)', 'MR Chart (移动极差图)'),
                           vertical_spacing=0.1)
        
        # I 图
        fig.add_trace(
            go.Scatter(y=data, mode='lines+markers', name='I', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_hline(y=I_limits['UCL'], line_dash="dash", line_color="red", name='UCL', row=1, col=1)
        fig.add_hline(y=I_limits['CL'], line_dash="solid", line_color="green", name='CL', row=1, col=1)
        fig.add_hline(y=I_limits['LCL'], line_dash="dash", line_color="red", name='LCL', row=1, col=1)
        
        # MR 图
        fig.add_trace(
            go.Scatter(y=mr, mode='lines+markers', name='MR', line=dict(color='blue')),
            row=2, col=1
        )
        fig.add_hline(y=MR_limits['UCL'], line_dash="dash", line_color="red", name='UCL', row=2, col=1)
        fig.add_hline(y=MR_limits['CL'], line_dash="solid", line_color="green", name='CL', row=2, col=1)
        fig.add_hline(y=MR_limits['LCL'], line_dash="dash", line_color="red", name='LCL', row=2, col=1)
        
        # 更新布局
        fig.update_layout(
            title='I-MR Control Chart (单值 - 移动极差控制图)',
            height=800,
            showlegend=True,
            legend=dict(x=1, xanchor='right', y=1)
        )
        
        # 保存图表
        fig.write_html(output_path)
        print(f"I-MR 图已保存到：{output_path}")
        
        return fig
    
    def plot_p_chart(self, defect_counts: np.ndarray, 
                     sample_sizes: np.ndarray,
                     output_path: str = 'p_chart.html') -> go.Figure:
        """
        绘制 P-Chart (不合格品率图)
        
        适用场景：计数型数据，不合格品率
        
        参数:
            defect_counts: 不合格品数量数组
            sample_sizes: 样本大小数组
            output_path: 输出文件路径
        
        返回:
            Plotly Figure 对象
        """
        # 计算不合格品率
        p = defect_counts / sample_sizes
        
        # 计算平均不合格品率
        p_bar = np.sum(defect_counts) / np.sum(sample_sizes)
        
        # 计算控制限 (每个样本的控制限可能不同)
        n_avg = np.mean(sample_sizes)
        std_p = np.sqrt(p_bar * (1 - p_bar) / n_avg)
        
        UCL = p_bar + 3 * std_p
        LCL = max(0, p_bar - 3 * std_p)  # LCL 不能为负
        
        # 创建图表
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(y=p, mode='lines+markers', name='p', line=dict(color='blue'))
        )
        fig.add_hline(y=UCL, line_dash="dash", line_color="red", name='UCL')
        fig.add_hline(y=p_bar, line_dash="solid", line_color="green", name='CL')
        fig.add_hline(y=LCL, line_dash="dash", line_color="red", name='LCL')
        
        # 更新布局
        fig.update_layout(
            title='P Control Chart (不合格品率控制图)',
            xaxis_title='Sample',
            yaxis_title='Proportion Defective',
            height=600,
            showlegend=True,
            legend=dict(x=1, xanchor='right', y=1)
        )
        
        # 保存图表
        fig.write_html(output_path)
        print(f"P-Chart 已保存到：{output_path}")
        
        return fig
    
    def check_western_electric_rules(self, data: np.ndarray, 
                                      limits: Dict) -> Dict[str, bool]:
        """
        检查 Western Electric Rules (6 条判异规则)
        
        参数:
            data: 数据数组
            limits: 控制限字典 (包含 UCL, CL, LCL, mean, std)
        
        返回:
            每条规则的违反情况字典
        """
        violations = {}
        
        # Rule 1: 单点超出±3σ
        violations['rule1'] = np.any((data > limits['UCL']) | (data < limits['LCL']))
        
        # Rule 2: 连续 9 点同侧
        above_mean = data > limits['mean']
        for i in range(len(data) - 8):
            if np.all(above_mean[i:i+9]) or np.all(~above_mean[i:i+9]):
                violations['rule2'] = True
                break
        else:
            violations['rule2'] = False
        
        # Rule 3: 连续 6 点上升/下降
        diff = np.diff(data)
        for i in range(len(diff) - 5):
            if np.all(diff[i:i+6] > 0) or np.all(diff[i:i+6] < 0):
                violations['rule3'] = True
                break
        else:
            violations['rule3'] = False
        
        # Rule 4: 连续 14 点交替
        if len(data) >= 14:
            alternating = True
            for i in range(len(data) - 13):
                pattern = data[i:i+14]
                diff = np.diff(pattern)
                signs = np.sign(diff)
                if np.all(signs[::2] == signs[0]) and np.all(signs[1::2] == -signs[0]):
                    violations['rule4'] = True
                    break
            else:
                violations['rule4'] = False
        else:
            violations['rule4'] = False
        
        # Rule 5: 连续 3 点中 2 点超出±2σ
        two_sigma_upper = limits['mean'] + 2 * limits['std']
        two_sigma_lower = limits['mean'] - 2 * limits['std']
        for i in range(len(data) - 2):
            points = data[i:i+3]
            count_outside = np.sum((points > two_sigma_upper) | (points < two_sigma_lower))
            if count_outside >= 2:
                violations['rule5'] = True
                break
        else:
            violations['rule5'] = False
        
        # Rule 6: 连续 5 点中 4 点超出±1σ
        one_sigma_upper = limits['mean'] + limits['std']
        one_sigma_lower = limits['mean'] - limits['std']
        for i in range(len(data) - 4):
            points = data[i:i+5]
            count_outside = np.sum((points > one_sigma_upper) | (points < one_sigma_lower))
            if count_outside >= 4:
                violations['rule6'] = True
                break
        else:
            violations['rule6'] = False
        
        return violations
    
    # ── Enhanced Capability & Alarm Engine ──────────────────────────
    
    def calculate_capability_indices(
        self,
        data: np.ndarray,
        usl: float,
        lsl: float,
        subgroup_size: Optional[int] = None,
    ) -> Dict:
        """
        计算完整的过程能力指数：Pp, Ppk, Cp, Cpk, PPM
        
        参数:
            data: 测量值数组
            usl: 规格上限 (Upper Spec Limit)
            lsl: 规格下限 (Lower Spec Limit)
            subgroup_size: 子组大小，用于计算 Cp/Cpk (within-subgroup σ)。
                          若为 None，只计算 Pp/Ppk (overall σ)。
        
        返回:
            {
                'Pp': float,           # 过程性能 (整体)
                'Ppk': float,          # 过程性能指数 (整体)
                'Pp_lower': float,     # Ppk 下限分量
                'Pp_upper': float,     # Ppk 上限分量
                'Cp': float | None,    # 过程能力 (组内)
                'Cpk': float | None,   # 过程能力指数 (组内)
                'Cpk_lower': float|None,
                'Cpk_upper': float|None,
                'sigma_overall': float,  # 整体标准差
                'sigma_within': float|None,  # 组内标准差
                'mean': float,
                'ppm_total': float,    # 预估总不良率 (PPM)
                'ppm_lower': float,
                'ppm_upper': float,
                'grade': str,          # 能力等级 (≥1.67优 / ≥1.33良 / ≥1.00可 / <1.00差)
                'usl': float,
                'lsl': float,
            }
        """
        n = len(data)
        if n < 2:
            return {"error": "数据点不足，至少需要 2 个点"}
        
        mean_v = float(np.mean(data))
        sigma_overall = float(np.std(data, ddof=1))  # 整体标准差 (用于 Pp/Ppk)
        
        if sigma_overall == 0:
            return {"error": "标准差为 0，无法计算能力指数"}
        
        spec_range = usl - lsl
        if spec_range <= 0:
            return {"error": f"规格范围无效: USL={usl}, LSL={lsl}"}
        
        # Pp / Ppk (整体性能指数)
        Pp = spec_range / (6 * sigma_overall)
        Ppk_upper = (usl - mean_v) / (3 * sigma_overall)
        Ppk_lower = (mean_v - lsl) / (3 * sigma_overall)
        Ppk = min(Ppk_upper, Ppk_lower)
        
        # PPM 预估 (基于正态分布假设)
        from scipy import stats as scipy_stats
        ppm_lower = scipy_stats.norm.cdf(lsl, mean_v, sigma_overall) * 1_000_000
        ppm_upper = (1 - scipy_stats.norm.cdf(usl, mean_v, sigma_overall)) * 1_000_000
        ppm_total = ppm_lower + ppm_upper
        
        # 能力等级
        min_idx = min(Pp, Ppk)
        if min_idx >= 1.67:
            grade = "🏆 优 (≥1.67)"
        elif min_idx >= 1.33:
            grade = "✅ 良 (≥1.33)"
        elif min_idx >= 1.00:
            grade = "⚠️ 可 (≥1.00)"
        else:
            grade = "❌ 差 (<1.00)"
        
        result = {
            "Pp": round(Pp, 4),
            "Ppk": round(Ppk, 4),
            "Ppk_lower": round(Ppk_lower, 4),
            "Ppk_upper": round(Ppk_upper, 4),
            "sigma_overall": round(sigma_overall, 4),
            "mean": round(mean_v, 4),
            "ppm_total": round(ppm_total, 1),
            "ppm_lower": round(ppm_lower, 1),
            "ppm_upper": round(ppm_upper, 1),
            "grade": grade,
            "usl": usl,
            "lsl": lsl,
        }
        
        # Cp / Cpk (组内能力指数 — 需要子组结构)
        if subgroup_size is not None and subgroup_size >= 2 and n >= subgroup_size * 2:
            n_subgroups = n // subgroup_size
            subgroup_ranges = []
            for i in range(n_subgroups):
                subgroup = data[i * subgroup_size:(i + 1) * subgroup_size]
                subgroup_ranges.append(float(np.max(subgroup) - np.min(subgroup)))
            
            # d2 常数表 (子组大小 2-10)
            d2_table = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326,
                        6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}
            d2 = d2_table.get(subgroup_size, 2.326)
            
            R_bar = np.mean(subgroup_ranges)
            sigma_within = R_bar / d2
            
            if sigma_within > 0:
                Cp = spec_range / (6 * sigma_within)
                Cpk_upper = (usl - mean_v) / (3 * sigma_within)
                Cpk_lower = (mean_v - lsl) / (3 * sigma_within)
                Cpk = min(Cpk_upper, Cpk_lower)
                
                result.update({
                    "Cp": round(Cp, 4),
                    "Cpk": round(Cpk, 4),
                    "Cpk_lower": round(Cpk_lower, 4),
                    "Cpk_upper": round(Cpk_upper, 4),
                    "sigma_within": round(sigma_within, 4),
                })
            else:
                result.update({"Cp": None, "Cpk": None, "Cpk_lower": None, "Cpk_upper": None, "sigma_within": None})
        else:
            result.update({"Cp": None, "Cpk": None, "Cpk_lower": None, "Cpk_upper": None, "sigma_within": None})
        
        return result
    
    def detect_alarms(
        self,
        data: np.ndarray,
        limits: Dict,
        usl: Optional[float] = None,
        lsl: Optional[float] = None,
        config: Optional[Dict] = None,
    ) -> Dict:
        """
        综合报警检测引擎
        
        检测规则:
          1. OOC  — 超出控制限 (±3σ)                 → 单点超限
          2. OOS  — 超出规格限 (USL/LSL)              → 不良品
          3. 连续单边  — 连续N点在同一侧               → 均值偏移
          4. 连续上升/下降 — 连续N点单调变化           → 趋势漂移
          5. 2-of-3 > 2σ                              → Western Electric Rule 5
          6. 4-of-5 > 1σ                              → Western Electric Rule 6
          7. 14点交替                                 → 系统周期性
        
        参数:
            data: 测量值数组
            limits: 控制限字典 (含 UCL, CL, LCL, mean, std)
            usl: 规格上限
            lsl: 规格下限
            config: 自定义规则参数 {'n_same_side': 9, 'n_trend': 6, ...}
        
        返回:
            {
                'summary': {'total_alarms': N, 'has_critical': bool, ...},
                'alarms': [{'index': i, 'type': 'OOC', 'severity': 'critical', 
                            'value': v, 'detail': '...'}, ...],
                'ooc_points': [...],    # 向后兼容
                'oos_points': [...],
                'trend_points': [...],
                'same_side_runs': [...],
                'violated_rules': {...},
            }
        """
        if config is None:
            config = {}
        
        n_same_side = config.get("n_same_side", 9)      # 默认连续9点同侧
        n_trend = config.get("n_trend", 6)               # 默认连续6点单调
        n_alternating = config.get("n_alternating", 14)  # 默认14点交替
        
        alarms = []
        ooc_points = []
        oos_points = []
        trend_points = []
        same_side_runs = []
        
        ucl = limits["UCL"]
        lcl = limits["LCL"]
        mean_v = limits["mean"]
        std_v = limits["std"]
        n = len(data)
        
        # ── Rule 1: OOC — 超出控制限 ──
        for i, v in enumerate(data):
            if v > ucl:
                detail = f"超出 UCL ({ucl:.3f})，值={v:.3f}，偏差={v - ucl:.3f}"
                alarms.append({"index": i, "type": "OOC", "subtype": "above_ucl",
                               "severity": "critical", "value": float(v), "detail": detail})
                ooc_points.append(i)
            elif v < lcl:
                detail = f"低于 LCL ({lcl:.3f})，值={v:.3f}，偏差={lcl - v:.3f}"
                alarms.append({"index": i, "type": "OOC", "subtype": "below_lcl",
                               "severity": "critical", "value": float(v), "detail": detail})
                ooc_points.append(i)
        
        # ── Rule 2: OOS — 超出规格限 ──
        if usl is not None:
            for i, v in enumerate(data):
                if v > usl:
                    detail = f"超出 USL ({usl})，值={v:.3f}"
                    alarms.append({"index": i, "type": "OOS", "subtype": "above_usl",
                                   "severity": "critical", "value": float(v), "detail": detail})
                    oos_points.append(i)
        if lsl is not None:
            for i, v in enumerate(data):
                if v < lsl:
                    detail = f"低于 LSL ({lsl})，值={v:.3f}"
                    alarms.append({"index": i, "type": "OOS", "subtype": "below_lsl",
                                   "severity": "critical", "value": float(v), "detail": detail})
                    oos_points.append(i)
        
        # ── Rule 3: 连续单边 (连续 N 点在同一侧) ──
        above_cl = data > mean_v
        run_start = 0
        for i in range(1, n):
            if above_cl[i] != above_cl[i - 1]:
                run_len = i - run_start
                if run_len >= n_same_side:
                    side = "上侧" if above_cl[run_start] else "下侧"
                    run_indices = list(range(run_start, i))
                    detail = f"连续 {run_len} 点在中心线{side} (≥{n_same_side}点)，提示均值偏移"
                    alarms.append({"index": run_start, "type": "连续单边",
                                   "subtype": "same_side_run",
                                   "severity": "warning",
                                   "run_length": run_len,
                                   "run_indices": run_indices,
                                   "side": side,
                                   "value": float(data[run_start]),
                                   "detail": detail})
                    same_side_runs.append({"start": run_start, "end": i - 1,
                                           "length": run_len, "side": side})
                run_start = i
        # 检查末尾
        run_len = n - run_start
        if run_len >= n_same_side:
            side = "上侧" if above_cl[run_start] else "下侧"
            run_indices = list(range(run_start, n))
            detail = f"连续 {run_len} 点在中心线{side} (≥{n_same_side}点)，提示均值偏移"
            alarms.append({"index": run_start, "type": "连续单边",
                           "subtype": "same_side_run",
                           "severity": "warning",
                           "run_length": run_len,
                           "run_indices": run_indices,
                           "side": side,
                           "value": float(data[run_start]),
                           "detail": detail})
            same_side_runs.append({"start": run_start, "end": n - 1,
                                   "length": run_len, "side": side})
        
        # ── Rule 4: 连续上升/下降 (连续 N 点单调变化) ──
        diff = np.diff(data)
        trend_start = 0
        for i in range(1, len(diff)):
            # 检查是否同方向
            if (diff[i] > 0 and diff[i-1] <= 0) or (diff[i] < 0 and diff[i-1] >= 0) or diff[i] == 0:
                trend_len = i - trend_start + 1  # +1 因为 diff 比 data 少1个
                if trend_len >= n_trend:
                    direction = "上升" if diff[trend_start] > 0 else "下降"
                    trend_indices = list(range(trend_start, trend_start + trend_len + 1))
                    detail = f"连续 {trend_len + 1} 点{direction} (≥{n_trend}点单调)，提示趋势漂移"
                    alarms.append({"index": trend_start, "type": "连续趋势",
                                   "subtype": "trend",
                                   "severity": "warning",
                                   "trend_length": trend_len + 1,
                                   "trend_indices": trend_indices,
                                   "direction": direction,
                                   "value": float(data[trend_start]),
                                   "detail": detail})
                    trend_points.append({"start": trend_start, "end": trend_start + trend_len,
                                         "length": trend_len + 1, "direction": direction})
                trend_start = i
        # 尾部检查
        trend_len = len(diff) - trend_start + 1
        if trend_len >= n_trend:
            direction = "上升" if diff[trend_start] > 0 else "下降"
            trend_indices = list(range(trend_start, n))
            detail = f"连续 {trend_len + 1} 点{direction} (≥{n_trend}点单调)，提示趋势漂移"
            alarms.append({"index": trend_start, "type": "连续趋势",
                           "subtype": "trend",
                           "severity": "warning",
                           "trend_length": trend_len + 1,
                           "trend_indices": trend_indices,
                           "direction": direction,
                           "value": float(data[trend_start]),
                           "detail": detail})
            trend_points.append({"start": trend_start, "end": n - 1,
                                 "length": trend_len + 1, "direction": direction})
        
        # ── Western Electric Rules 补充 ──
        # Rule 5: 连续3点中2点超出±2σ
        two_sigma_upper = mean_v + 2 * std_v
        two_sigma_lower = mean_v - 2 * std_v
        for i in range(n - 2):
            points = data[i:i+3]
            count = np.sum((points > two_sigma_upper) | (points < two_sigma_lower))
            if count >= 2:
                detail = f"连续 3 点中 {count} 点超出 ±2σ (索引 {i}-{i+2})"
                alarms.append({"index": i, "type": "Western Electric",
                               "subtype": "rule5_2of3_2sigma",
                               "severity": "warning",
                               "value": float(data[i]),
                               "detail": detail})
        
        # Rule 6: 连续5点中4点超出±1σ
        one_sigma_upper = mean_v + std_v
        one_sigma_lower = mean_v - std_v
        for i in range(n - 4):
            points = data[i:i+5]
            count = np.sum((points > one_sigma_upper) | (points < one_sigma_lower))
            if count >= 4:
                detail = f"连续 5 点中 {count} 点超出 ±1σ (索引 {i}-{i+4})"
                alarms.append({"index": i, "type": "Western Electric",
                               "subtype": "rule6_4of5_1sigma",
                               "severity": "info",
                               "value": float(data[i]),
                               "detail": detail})
        
        # ── 汇总 ──
        critical_count = sum(1 for a in alarms if a["severity"] == "critical")
        warning_count = sum(1 for a in alarms if a["severity"] == "warning")
        info_count = sum(1 for a in alarms if a["severity"] == "info")
        
        # 违反的规则统计
        violated_rules = {
            "OOC (超控制限)": len(ooc_points),
            "OOS (超规格限)": len(oos_points),
            "连续单边": len(same_side_runs),
            "连续趋势": len(trend_points),
            "Western Electric R5 (2/3>2σ)": sum(1 for a in alarms if a.get("subtype") == "rule5_2of3_2sigma"),
            "Western Electric R6 (4/5>1σ)": sum(1 for a in alarms if a.get("subtype") == "rule6_4of5_1sigma"),
        }
        
        return {
            "summary": {
                "total_alarms": len(alarms),
                "critical": critical_count,
                "warning": warning_count,
                "info": info_count,
                "status": "🔴 Critical" if critical_count > 0 else ("🟡 Warning" if warning_count > 0 else "🟢 Normal"),
            },
            "alarms": alarms,
            "ooc_points": ooc_points,
            "oos_points": oos_points,
            "trend_points": trend_points,
            "same_side_runs": same_side_runs,
            "violated_rules": violated_rules,
        }
    
    def run_demo(self):
        """运行示例演示"""
        print("=" * 60)
        print("SPC Control Charts Demo (SPC 控制图演示)")
        print("=" * 60)
        
        # 生成模拟数据
        np.random.seed(42)
        n_subgroups = 25
        subgroup_size = 5
        
        # 正常过程数据
        normal_data = np.random.normal(loc=100, scale=5, size=(n_subgroups, subgroup_size))
        
        # 异常过程数据 (从第 20 组开始偏移)
        abnormal_data = np.random.normal(loc=100, scale=5, size=(n_subgroups, subgroup_size))
        abnormal_data[20:] += 8  # 均值偏移
        
        print("\n1. 生成 X-bar R 图 (正常过程)...")
        self.plot_xbar_r(
            pd.DataFrame(normal_data),
            output_path='xbar_r_normal.html'
        )
        
        print("\n2. 生成 X-bar R 图 (异常过程)...")
        self.plot_xbar_r(
            pd.DataFrame(abnormal_data),
            output_path='xbar_r_abnormal.html'
        )
        
        print("\n3. 生成 I-MR 图...")
        imr_data = np.random.normal(loc=50, scale=3, size=50)
        self.plot_imr(imr_data, output_path='imr_chart.html')
        
        print("\n4. 生成 P-Chart...")
        defect_counts = np.random.binomial(n=100, p=0.05, size=25)
        sample_sizes = np.full(25, 100)
        self.plot_p_chart(defect_counts, sample_sizes, output_path='p_chart.html')
        
        print("\n5. Western Electric Rules 检查...")
        limits = self.calculate_control_limits(abnormal_data.flatten())
        violations = self.check_western_electric_rules(abnormal_data.flatten(), limits)
        
        print("\nWestern Electric Rules 检查结果:")
        print("-" * 40)
        for rule, violated in violations.items():
            status = "❌ 违反" if violated else "✅ 正常"
            print(f"{rule}: {self.western_electric_rules[rule]} - {status}")
        
        print("\n" + "=" * 60)
        print("Demo 完成！请查看生成的 HTML 文件。")
        print("=" * 60)


if __name__ == '__main__':
    spc = SPCControlCharts()
    spc.run_demo()
