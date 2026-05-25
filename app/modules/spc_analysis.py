"""YMS Spc Analysis Module."""
import streamlit as st
from cache_utils import cached_static_query, cached_aggregate_query, cached_list_query, cached_detail_query
from database import run_query
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def render():
    """Render the spc_analysis page."""
    st.title("📈 SPC Control Chart Analysis")
    
    
    # Get available parameters
    
    params_df = cached_static_query("SELECT DISTINCT Parameter_Name, Lot_ID FROM Measurements ORDER BY Parameter_Name")
    
    if params_df.empty:
    
        st.warning("No measurement data. Please upload data first.")
    
        st.stop()
    
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
    
        param = st.selectbox("Parameter", params_df["Parameter_Name"].unique().tolist())
    
    with c2:
    
        lot_filter = st.selectbox("Lot Filter", ["All"] + params_df["Lot_ID"].unique().tolist())
    
    with c3:
    
        chart_type = st.selectbox("Chart Type", ["I-MR (单值-移动极差)", "X-bar R (均值-极差)"],
    
                                  help="I-MR: 适合连续单值数据 | X-bar R: 需要子组结构")
    
    
    # ── Spec Limits ──
    
    st.markdown("#### 📏 Specification Limits (规格界限)")
    
    sc1, sc2, sc3 = st.columns(3)
    
    with sc1:
    
        usl_input = st.number_input("USL (规格上限)", value=0.0, step=0.01,
    
                                    help="输入产品规格上限。留0则自动从数据推算。")
    
    with sc2:
    
        lsl_input = st.number_input("LSL (规格下限)", value=0.0, step=0.01,
    
                                    help="输入产品规格下限。留0则自动从数据推算。")
    
    with sc3:
    
        subgroup_size = st.number_input("子组大小 (Cp/Cpk用)", min_value=0, max_value=25, value=0,
    
                                        help="0=不计算Cp/Cpk；≥2则用R-bar/d2法估算组内σ。")
    
    
    # Query data
    
    if lot_filter == "All":
    
        df = cached_detail_query("SELECT * FROM Measurements WHERE Parameter_Name = ? ORDER BY Timestamp", [param])
    
    else:
    
        df = cached_detail_query("SELECT * FROM Measurements WHERE Parameter_Name = ? AND Lot_ID = ? ORDER BY Timestamp", [param, lot_filter])
    
    
    if df.empty:
    
        st.warning("No data for selected filters.")
    
        st.stop()
    
    
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    
    values = df["Value"].values
    
    n = len(values)
    
    
    # ── Import SPC engine ──
    
    import importlib.util
    
    _spc_path = os.path.join(os.path.dirname(__file__), "..", "src", "yms", "analysis", "spc_control_charts.py")
    
    _spc_spec = importlib.util.spec_from_file_location("spc_control_charts", os.path.abspath(_spc_path))
    
    _spc_mod = importlib.util.module_from_spec(_spc_spec)
    
    _spc_spec.loader.exec_module(_spc_mod)
    
    spc = _spc_mod.SPCControlCharts()
    
    
    # Calculate control limits
    
    limits = spc.calculate_control_limits(values)
    
    mean_v = limits["mean"]
    
    std_v = limits["std"]
    
    ucl = limits["UCL"]
    
    lcl = limits["LCL"]
    
    
    # ── Spec limits: use input or auto-infer ──
    
    if usl_input != 0.0 or lsl_input != 0.0:
    
        usl = usl_input if usl_input != 0.0 else None
    
        lsl = lsl_input if lsl_input != 0.0 else None
    
    else:
    
        # Auto: use ±4σ as default spec range
    
        usl = mean_v + 4 * std_v
    
        lsl = mean_v - 4 * std_v
    
        st.caption(f"💡 USL/LSL 未设定，自动使用 ±4σ：USL={usl:.3f}，LSL={lsl:.3f}。请根据产品规格手动设定。")
    
    
    # ── Capability Analysis ──
    
    if usl is not None and lsl is not None:
    
        sg = int(subgroup_size) if subgroup_size >= 2 else None
    
        cap = spc.calculate_capability_indices(values, usl, lsl, subgroup_size=sg)
    
        has_cap = "error" not in cap
    
    else:
    
        # Only one side spec
    
        if usl is not None:
    
            cap_temp = spc.calculate_capability_indices(values, usl, mean_v - 10 * std_v, subgroup_size=None)
    
        else:
    
            cap_temp = spc.calculate_capability_indices(values, mean_v + 10 * std_v, lsl, subgroup_size=None)
    
        cap = cap_temp
    
        has_cap = "error" not in cap
    
    
    # ── Alarm Detection ──
    
    alarm_config = {
    
        "n_same_side": st.session_state.get("spc_n_same_side", 9),
    
        "n_trend": st.session_state.get("spc_n_trend", 6),
    
    }
    
    alarm_result = spc.detect_alarms(values, limits, usl=usl, lsl=lsl, config=alarm_config)
    
    
    # ═══════════════════════════════════════════════════════
    
    #  Row 1: Capability Indices
    
    # ═══════════════════════════════════════════════════════
    
    st.markdown("---")
    
    st.subheader("📊 Process Capability (过程能力)")
    
    
    if has_cap:
    
        c1, c2, c3, c4, c5, c6 = st.columns(6)
    
        c1.metric("Pp", f"{cap['Pp']:.3f}", help="过程性能 (整体标准差)")
    
        c2.metric("Ppk", f"{cap['Ppk']:.3f}", delta=None,
    
                  help=f"Ppk_upper={cap['Ppk_upper']:.3f} | Ppk_lower={cap['Ppk_lower']:.3f}")
    
        if cap.get("Cp") is not None:
    
            c3.metric("Cp", f"{cap['Cp']:.3f}", help="过程能力 (组内标准差)")
    
            c4.metric("Cpk", f"{cap['Cpk']:.3f}", help=f"Cpk_upper={cap['Cpk_upper']:.3f} | Cpk_lower={cap['Cpk_lower']:.3f}")
    
        else:
    
            c3.metric("Cp", "—", help="需设子组大小")
    
            c4.metric("Cpk", "—", help="需设子组大小")
    
        c5.metric("PPM", f"{cap['ppm_total']:.0f}",
    
                  help=f"超上限: {cap['ppm_upper']:.0f} | 超下限: {cap['ppm_lower']:.0f}")
    
        c6.metric("Grade", cap["grade"], help="≥1.67优 / ≥1.33良 / ≥1.0可 / <1.0差")
    
    
        # Capability gauge visualization
    
        st.caption(f"σ_overall={cap['sigma_overall']:.4f} | μ={cap['mean']:.4f} | "
    
                   f"USL={cap['usl']} | LSL={cap['lsl']}")
    
    else:
    
        st.warning(f"⚠️ 无法计算能力指数：{cap.get('error', '未知错误')}")
    
    
    # ═══════════════════════════════════════════════════════
    
    #  Row 2: Alarm Summary
    
    # ═══════════════════════════════════════════════════════
    
    st.markdown("---")
    
    st.subheader("🚨 Alarm Rules (报警规则)")
    
    
    alarm_summary = alarm_result["summary"]
    
    ac1, ac2, ac3, ac4 = st.columns(4)
    
    ac1.metric("Status", alarm_summary["status"])
    
    ac2.metric("Total Alarms", alarm_summary["total_alarms"])
    
    ac3.metric("🔴 Critical", alarm_summary["critical"])
    
    ac4.metric("🟡 Warning", alarm_summary["warning"])
    
    
    # Violated rules detail
    
    with st.expander("📋 报警规则详情", expanded=(alarm_summary["total_alarms"] > 0)):
    
        violated = alarm_result["violated_rules"]
    
        for rule_name, count in violated.items():
    
            if count > 0:
    
                st.markdown(f"- **{rule_name}**: {count} 次违反")
    
            else:
    
                st.markdown(f"- {rule_name}: ✅ 正常")
    
    
        # Alarm detail table
    
        alarms = alarm_result["alarms"]
    
        if alarms:
    
            st.markdown("---")
    
            alarm_rows = []
    
            for a in alarms:
    
                severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(a["severity"], "")
    
                alarm_rows.append({
    
                    "严重度": severity_icon,
    
                    "类型": a["type"],
    
                    "索引": a["index"],
    
                    "值": f"{a['value']:.3f}",
    
                    "详情": a["detail"],
    
                })
    
            st.dataframe(pd.DataFrame(alarm_rows), use_container_width=True, hide_index=True)
    
    
    # ═══════════════════════════════════════════════════════
    
    #  Row 3: Control Chart
    
    # ═══════════════════════════════════════════════════════
    
    st.markdown("---")
    
    st.subheader("📈 Control Chart (控制图)")
    
    
    # Build point colors: red=OOC, orange=OOS, blue=trend, steelblue=normal
    
    ooc_set = set(alarm_result["ooc_points"])
    
    oos_set = set(alarm_result["oos_points"])
    
    # Collect trend indices
    
    trend_set = set()
    
    for tp in alarm_result["trend_points"]:
    
        for idx in range(tp["start"], tp["end"] + 1):
    
            trend_set.add(idx)
    
    # Collect same-side run indices
    
    side_set = set()
    
    for sr in alarm_result["same_side_runs"]:
    
        for idx in range(sr["start"], sr["end"] + 1):
    
            side_set.add(idx)
    
    
    colors = []
    
    annotations = []
    
    for i in range(n):
    
        if i in ooc_set:
    
            colors.append("red")
    
            annotations.append(dict(x=df["Timestamp"].iloc[i], y=float(values[i]),
    
                                    text="OOC", showarrow=True, arrowhead=2,
    
                                    font=dict(color="red", size=10), ax=0, ay=-25))
    
        elif i in oos_set:
    
            colors.append("darkorange")
    
            annotations.append(dict(x=df["Timestamp"].iloc[i], y=float(values[i]),
    
                                    text="OOS", showarrow=True, arrowhead=2,
    
                                    font=dict(color="darkorange", size=10), ax=0, ay=-25))
    
        elif i in trend_set:
    
            colors.append("mediumblue")
    
        elif i in side_set:
    
            colors.append("goldenrod")
    
        else:
    
            colors.append("steelblue")
    
    
    fig = go.Figure()
    
    
    # Main trace
    
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=values, mode="lines+markers",
    
                             marker=dict(color=colors, size=7, line=dict(width=1, color="white")),
    
                             name=param, hovertemplate="%{y:.3f}<br>%{x}"))
    
    
    # Control limits
    
    fig.add_hline(y=ucl, line_dash="dash", line_color="red", line_width=1.5,
    
                  annotation_text=f"UCL ({ucl:.3f})", annotation_position="top right")
    
    fig.add_hline(y=lcl, line_dash="dash", line_color="red", line_width=1.5,
    
                  annotation_text=f"LCL ({lcl:.3f})", annotation_position="bottom right")
    
    fig.add_hline(y=mean_v + 2 * std_v, line_dash="dot", line_color="orange", line_width=1,
    
                  annotation_text="+2σ")
    
    fig.add_hline(y=mean_v - 2 * std_v, line_dash="dot", line_color="orange", line_width=1,
    
                  annotation_text="-2σ")
    
    fig.add_hline(y=mean_v, line_dash="solid", line_color="green", line_width=1.5,
    
                  annotation_text=f"CL ({mean_v:.3f})")
    
    
    # Spec limits (if set)
    
    if usl is not None:
    
        fig.add_hline(y=usl, line_dash="dashdot", line_color="purple", line_width=1.5,
    
                      annotation_text=f"USL ({usl:.3f})")
    
    if lsl is not None:
    
        fig.add_hline(y=lsl, line_dash="dashdot", line_color="purple", line_width=1.5,
    
                      annotation_text=f"LSL ({lsl:.3f})")
    
    
    # Trend shading — use add_shape for robustness
    
    for tp in alarm_result["trend_points"]:
    
        t_start = df["Timestamp"].iloc[tp["start"]]
    
        t_end = df["Timestamp"].iloc[tp["end"]]
    
        shade_color = "rgba(0,0,255,0.08)" if tp["direction"] == "上升" else "rgba(255,0,0,0.08)"
    
        fig.add_shape(type="rect", x0=t_start, x1=t_end, y0=0, y1=1,
    
                      xref="x", yref="paper", fillcolor=shade_color, line_width=0, layer="below")
    
        fig.add_annotation(x=t_start, y=1.02, xref="x", yref="paper",
    
                          text=f"{tp['direction']}趋势", showarrow=False,
    
                          font=dict(size=9, color="gray"), xanchor="left")
    
    
    # Same-side run shading
    
    for i, sr in enumerate(alarm_result["same_side_runs"]):
    
        t_start = df["Timestamp"].iloc[sr["start"]]
    
        t_end = df["Timestamp"].iloc[sr["end"]]
    
        fig.add_shape(type="rect", x0=t_start, x1=t_end, y0=0, y1=1,
    
                      xref="x", yref="paper", fillcolor="rgba(255,215,0,0.10)",
    
                      line=dict(width=1, dash="dot", color="goldenrod"), layer="below")
    
        fig.add_annotation(x=t_start, y=-0.12 - i * 0.06, xref="x", yref="paper",
    
                          text=f"连续{sr['length']}点{sr['side']}", showarrow=False,
    
                          font=dict(size=9, color="#b8860b"), xanchor="left")
    
    
    fig.update_layout(
    
        height=500,
    
        title=f"SPC Control Chart — {param} (n={n})",
    
        xaxis_title="Timestamp",
    
        yaxis_title="Value",
    
        hovermode="x unified",
    
        annotations=annotations if len(annotations) <= 20 else annotations[:20],
    
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(128,128,128,0.15)")
    
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(128,128,128,0.15)")
    
    st.plotly_chart(fig, use_container_width=True)
    
    
    # ── Legend ──
    
    st.caption("🔴 OOC (超控制限) | 🟠 OOS (超规格限) | 🔵 趋势点 | 🟡 连续单边 | 🔵 正常")
    
    
    # ═══════════════════════════════════════════════════════
    
    #  Row 4: Alarm Configuration & Distribution
    
    # ═══════════════════════════════════════════════════════
    
    col_left, col_right = st.columns([1, 2])
    
    
    with col_left:
    
        st.markdown("#### ⚙️ 报警规则配置")
    
        n_side = st.slider("连续单边阈值", min_value=5, max_value=15, value=9,
    
                           help="连续N点在中心线同一侧视为均值偏移")
    
        n_tr = st.slider("连续趋势阈值", min_value=4, max_value=10, value=6,
    
                         help="连续N点单调上升或下降视为趋势漂移")
    
        if st.button("🔄 重新分析"):
    
            st.session_state["spc_n_same_side"] = n_side
    
            st.session_state["spc_n_trend"] = n_tr
    
            st.rerun()
    
    
    with col_right:
    
        st.markdown("#### 📊 Distribution Histogram")
    
        fig2 = go.Figure()
    
        fig2.add_trace(go.Histogram(x=values, nbinsx=min(40, max(10, n // 5)),
    
                                     marker_color="steelblue", opacity=0.7,
    
                                     name="Frequency"))
    
        # Overlay normal curve
    
        if std_v > 0:
    
            x_range = np.linspace(mean_v - 4 * std_v, mean_v + 4 * std_v, 200)
    
            from scipy import stats as scipy_stats
    
            pdf = scipy_stats.norm.pdf(x_range, mean_v, std_v)
    
            scale = n * (x_range[1] - x_range[0])
    
            fig2.add_trace(go.Scatter(x=x_range, y=pdf * scale, mode="lines",
    
                                       line=dict(color="red", width=2, dash="dash"),
    
                                       name="Normal Fit"))
    
    
        fig2.add_vline(x=mean_v, line_dash="solid", line_color="green", line_width=2,
    
                       annotation_text=f"μ={mean_v:.3f}")
    
        fig2.add_vline(x=ucl, line_dash="dash", line_color="red", annotation_text="UCL")
    
        fig2.add_vline(x=lcl, line_dash="dash", line_color="red", annotation_text="LCL")
    
        if usl is not None:
    
            fig2.add_vline(x=usl, line_dash="dashdot", line_color="purple", annotation_text="USL")
    
        if lsl is not None:
    
            fig2.add_vline(x=lsl, line_dash="dashdot", line_color="purple", annotation_text="LSL")
    
    
        fig2.update_layout(height=350, title=f"Distribution of {param} (σ={std_v:.4f})",
    
                           bargap=0.05)
    
        st.plotly_chart(fig2, use_container_width=True)
    
    
    # ── Data table ──
    
    with st.expander("📋 原始数据", expanded=False):
    
        st.dataframe(df[["Timestamp", "Value", "Lot_ID", "Recipe"]], use_container_width=True)
    
    
    
    # ═══════════════════════════════════════════════════════════
    
    #  Module 4: Wafer Map
    
    # ═══════════════════════════════════════════════════════════
