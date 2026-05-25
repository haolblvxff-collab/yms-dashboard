"""YMS Wafer Map Module."""
import streamlit as st
from cache_utils import cached_static_query, cached_aggregate_query, cached_list_query, cached_detail_query
from database import run_query
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import plotly.express as px

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def render():
    """Render the wafer_map page."""
    st.title("🗺️ Wafer Map Visualization")
    
    
    # ── Wafer config ──
    
    WAFER_SIZES = {
    
        "2 inch (50.8mm)": 25.4,
    
        "3 inch (76.2mm)": 38.1,
    
        "4 inch (100mm)":  50.0,
    
        "6 inch (150mm)":  75.0,
    
        "8 inch (200mm)": 100.0,
    
        "12 inch (300mm)": 150.0,
    
    }
    
    FLAT_RATIOS = {  # flat_length / diameter
    
        "2 inch (50.8mm)": 0.30,
    
        "3 inch (76.2mm)": 0.25,
    
        "4 inch (100mm)":  0.22,
    
        "6 inch (150mm)":  0.20,
    
        "8 inch (200mm)":  0.18,
    
        "12 inch (300mm)": 0.13,
    
    }
    
    
    ctl1, ctl2, ctl3 = st.columns(3)
    
    with ctl1:
    
        wafer_type = st.radio("Edge Type", ["🔽 Notch", "➖ Flat"], horizontal=True)
    
    with ctl2:
    
        wafer_size = st.selectbox("Wafer Size", list(WAFER_SIZES.keys()), index=5)
    
    with ctl3:
    
        compare = st.checkbox("Compare 2 Sizes", value=False)
    
    
    radius_mm = WAFER_SIZES[wafer_size]
    
    flat_ratio = FLAT_RATIOS[wafer_size]
    
    
    if compare:
    
        compare_size = st.selectbox("Compare with", list(WAFER_SIZES.keys()), index=2)
    
        radius_cmp = WAFER_SIZES[compare_size]
    
        flat_cmp = FLAT_RATIOS[compare_size]
    
        # Scale factor for reuse of same defect coordinates
    
        scale_cmp = radius_cmp / 150.0
    
    scale = radius_mm / 150.0
    
    
    defect_df = cached_list_query("SELECT * FROM Defects ORDER BY Timestamp DESC LIMIT 500")
    
    if defect_df.empty:
    
        st.warning("No defect data. Upload defect data first.")
    
        st.stop()
    
    
    lot_filter = st.selectbox("Lot ID", ["All"] + defect_df["Lot_ID"].unique().tolist())
    
    if lot_filter != "All":
    
        defect_df = defect_df[defect_df["Lot_ID"] == lot_filter]
    
    
    # ── Helper: draw one wafer ──
    
    def draw_wafer_figure(wdf, r_mm, w_type, flat_r, title_suffix=""):
    
        fig = go.Figure()
    
        margin = r_mm * 1.15
    
    
        # Wafer circle
    
        theta = np.linspace(0, 2 * np.pi, 300)
    
        fig.add_trace(go.Scatter(
    
            x=r_mm * np.cos(theta), y=r_mm * np.sin(theta),
    
            mode="lines", line=dict(color="#555", width=1.5),
    
            name="Edge", showlegend=False,
    
        ))
    
    
        if w_type == "🔽 Notch":
    
            # Notch at top: small V cut
    
            nx, ny = 0, r_mm  # top of circle
    
            nd = r_mm * 0.04   # notch depth
    
            nw = r_mm * 0.025  # notch half-width
    
            fig.add_trace(go.Scatter(
    
                x=[-nw, 0, nw], y=[ny - nd, ny, ny - nd],
    
                mode="lines", line=dict(color="#555", width=2),
    
                fill="toself", fillcolor="white",
    
                name="Notch", showlegend=False,
    
            ))
    
        else:
    
            # Flat at bottom: chord
    
            flat_half = flat_r * r_mm  # half flat length
    
            flat_y = -np.sqrt(r_mm**2 - flat_half**2)  # y coord of flat chord
    
            fig.add_trace(go.Scatter(
    
                x=[-flat_half, flat_half], y=[flat_y, flat_y],
    
                mode="lines", line=dict(color="#555", width=2.5),
    
                name="Flat", showlegend=False,
    
            ))
    
            # Dashed arc to show cut-off portion (optional, subtle)
    
            arc_theta = np.arccos(flat_y / r_mm) if abs(flat_y/r_mm) <= 1 else 0
    
            if arc_theta > 0.05:
    
                cut_theta = np.linspace(np.pi - arc_theta, np.pi + arc_theta, 50)
    
                fig.add_trace(go.Scatter(
    
                    x=r_mm * np.cos(cut_theta), y=r_mm * np.sin(cut_theta),
    
                    mode="lines", line=dict(color="#ccc", width=1, dash="dot"),
    
                    showlegend=False,
    
                ))
    
    
        # Defect points
    
        if not wdf.empty:
    
            for dtype in sorted(wdf["Defect_Type"].unique()):
    
                subset = wdf[wdf["Defect_Type"] == dtype]
    
                fig.add_trace(go.Scatter(
    
                    x=subset["X"], y=subset["Y"], mode="markers",
    
                    name=dtype,
    
                    marker=dict(size=5, opacity=0.55, line=dict(width=0)),
    
                ))
    
    
        title = f"Wafer Map{title_suffix}"
    
        fig.update_layout(
    
            title=title,
    
            xaxis=dict(scaleanchor="y", scaleratio=1, title="X (mm)",
    
                       range=[-margin, margin], showgrid=False, zeroline=False),
    
            yaxis=dict(title="Y (mm)", range=[-margin, margin],
    
                       showgrid=False, zeroline=False),
    
            height=480,
    
            legend=dict(orientation="h", yanchor="bottom", y=-0.18,
    
                        xanchor="center", x=0.5),
    
            margin=dict(l=10, r=10, t=40, b=10),
    
        )
    
        return fig
    
    
    # ── Generate defect data (base 12" coords, then scale) ──
    
    np.random.seed(42)
    
    wafer_data = []
    
    base_radius = 150.0
    
    for _, row in defect_df.iterrows():
    
        r = np.random.uniform(0.08, 0.95) * base_radius
    
        angle = np.random.uniform(0, 2 * np.pi)
    
        base_x = r * np.cos(angle)
    
        base_y = r * np.sin(angle)
    
        count = max(1, int(row["Count"]))
    
        jitter_sigma = 4.0
    
        for _ in range(count):
    
            jx = base_x + np.random.normal(0, jitter_sigma)
    
            jy = base_y + np.random.normal(0, jitter_sigma)
    
            dist = np.sqrt(jx**2 + jy**2)
    
            clamp_r = base_radius * 0.95
    
            if dist > clamp_r:
    
                jx *= clamp_r / dist
    
                jy *= clamp_r / dist
    
            wafer_data.append({
    
                "X": jx, "Y": jy,
    
                "Defect_Type": row["Defect_Type"],
    
                "Wafer_ID": row["Wafer_ID"],
    
                "Severity": row["Severity"],
    
            })
    
    wdf_base = pd.DataFrame(wafer_data)
    
    
    # Scale to selected wafer
    
    wdf_main = wdf_base.copy()
    
    wdf_main["X"] *= scale
    
    wdf_main["Y"] *= scale
    
    
    if compare:
    
        wdf_cmp = wdf_base.copy()
    
        wdf_cmp["X"] *= scale_cmp
    
        wdf_cmp["Y"] *= scale_cmp
    
    
        col_left, col_right = st.columns(2)
    
        with col_left:
    
            fig_a = draw_wafer_figure(wdf_main, radius_mm, wafer_type, flat_ratio,
    
                                      title_suffix=f" — {wafer_size}")
    
            st.plotly_chart(fig_a, use_container_width=True)
    
        with col_right:
    
            fig_b = draw_wafer_figure(wdf_cmp, radius_cmp, wafer_type, flat_cmp,
    
                                      title_suffix=f" — {compare_size}")
    
            st.plotly_chart(fig_b, use_container_width=True)
    
    else:
    
        fig = draw_wafer_figure(wdf_main, radius_mm, wafer_type, flat_ratio,
    
                                title_suffix=f" — {lot_filter if lot_filter != 'All' else 'All Lots'}")
    
        st.plotly_chart(fig, use_container_width=True)
    
    
    # ── Summary sidebar ──
    
    st.markdown("---")
    
    csum1, csum2 = st.columns(2)
    
    with csum1:
    
        st.subheader("Defect Summary by Type")
    
        summary = defect_df.groupby("Defect_Type").agg(
    
            Total=("Count", "sum"),
    
            Sites=("Defect_Type", "count"),
    
        ).reset_index()
    
        summary.columns = ["Defect Type", "Total Count", "Sites"]
    
        st.dataframe(summary, use_container_width=True, hide_index=True)
    
    with csum2:
    
        st.subheader("By Severity")
    
        sev = defect_df.groupby("Severity")["Count"].sum().reset_index()
    
        sev.columns = ["Severity", "Total Count"]
    
        if not sev.empty:
    
            fig_sev = px.pie(sev, names="Severity", values="Total Count", hole=0.4,
    
                             color_discrete_sequence=["#2ecc71", "#f39c12", "#e74c3c", "#8e44ad"])
    
            st.plotly_chart(fig_sev, use_container_width=True)
    
    
    
    # ═══════════════════════════════════════════════════════════
    
    #  Module 5: Lot Gantt
    
    # ═══════════════════════════════════════════════════════════
