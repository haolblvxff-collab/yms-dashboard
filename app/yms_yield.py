"""
YMS Yield Analysis — Streamlit UI
==================================
Defect Pareto, Yield Loss Decomposition, Defect Density Trend, Kill Ratio.
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import importlib.util

# ── Import engine ──
_eng_path = os.path.join(os.path.dirname(__file__), "..", "src", "yms", "analysis", "yield_analysis.py")
_spec = importlib.util.spec_from_file_location("yield_analysis", os.path.abspath(_eng_path))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
YieldAnalysis = _mod.YieldAnalysis

yield_eng = YieldAnalysis()


def render_yield_page(db_run_query=None):
    """Render yield analysis Streamlit page."""
    st.title("📉 Yield Analysis")
    st.caption("Defect Pareto · Yield Loss · Density Trend · Kill Ratio")

    if db_run_query is None:
        st.error("Database connection not available.")
        return

    # ── Load data ──
    lots_df = db_run_query("SELECT * FROM Lots")
    defects_df = db_run_query("SELECT * FROM Defects")

    if lots_df.empty and defects_df.empty:
        st.warning("No data. Upload data first via Data Upload page.")
        return

    # ── Config ──
    st.markdown("### ⚙️ Configuration")
    c1, c2, c3 = st.columns(3)
    with c1:
        dice_per_wafer = st.number_input("Dice per Wafer", 100, 100000, 1000, 100,
                                          help="Total dice per wafer for kill ratio and DLY calculation.")
    with c2:
        wafers_per_lot = st.number_input("Wafers per Lot", 1, 50, 25,
                                          help="Average wafers per lot.")
    with c3:
        top_n = st.slider("Top N Categories", 5, 30, 15,
                           help="Number of top defect types to show.")

    if not st.button("▶️ Run Yield Analysis", use_container_width=True):
        st.info("Configure above and click Run.")
        return

    # ── Run Analysis ──
    report = yield_eng.analyze(lots_df, defects_df,
                                total_dice_per_wafer=dice_per_wafer,
                                n_wafers_per_lot=wafers_per_lot)

    # ── KPI Row ──
    st.markdown("---")
    st.markdown("### 📊 Yield Summary")
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Lots", report.total_lots)
    with k2:
        st.metric("Total Defects", f"{report.total_defects:,}")
    with k3:
        yield_color = "normal" if report.overall_yield >= 90 else "off"
        st.metric("Lot Completion", f"{report.overall_yield:.1f}%", delta_color=yield_color)
    with k4:
        defects_per_lot = report.total_defects / max(report.total_lots, 1)
        st.metric("Avg Defects/Lot", f"{defects_per_lot:.0f}")
    with k5:
        st.metric("Est. Kill Ratio", f"{report.kill_ratio:.2f}")

    # ── Charts Tabs ──
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Defect Pareto", "📉 Yield Loss", "📈 Density Trend", "🎯 Kill Ratio"
    ])

    with tab1:
        if report.pareto_df is not None and not report.pareto_df.empty:
            pareto = report.pareto_df.head(top_n)
            st.plotly_chart(yield_eng.build_pareto_chart(pareto), use_container_width=True)
            with st.expander("📋 Pareto Table", expanded=False):
                st.dataframe(pareto, use_container_width=True, hide_index=True)
        else:
            st.info("No defect data for Pareto analysis.")

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            if report.loss_by_type is not None and not report.loss_by_type.empty:
                loss = report.loss_by_type.head(top_n)
                st.plotly_chart(yield_eng.build_loss_waterfall(loss), use_container_width=True)
            else:
                st.info("No data for yield loss decomposition.")
        with col_b:
            if report.loss_by_type is not None and not report.loss_by_type.empty:
                st.markdown("#### Yield Loss Table")
                st.dataframe(report.loss_by_type.head(top_n), use_container_width=True, hide_index=True)
            if report.loss_by_severity is not None and not report.loss_by_severity.empty:
                st.markdown("#### By Severity")
                st.dataframe(report.loss_by_severity, use_container_width=True, hide_index=True)

    with tab3:
        if report.density_trend is not None and not report.density_trend.empty:
            st.plotly_chart(yield_eng.build_density_trend_chart(report.density_trend),
                            use_container_width=True)
            with st.expander("📋 Trend Data", expanded=False):
                st.dataframe(report.density_trend, use_container_width=True, hide_index=True)
        else:
            st.info("No trend data available.")

    with tab4:
        col_c, col_d = st.columns([3, 2])
        with col_c:
            if report.kill_by_type is not None and not report.kill_by_type.empty:
                st.plotly_chart(yield_eng.build_kill_ratio_chart(report.kill_by_type),
                                use_container_width=True)
            else:
                st.info("No kill ratio data available.")
        with col_d:
            st.markdown("#### Kill Ratio Table")
            if report.kill_by_type is not None and not report.kill_by_type.empty:
                st.dataframe(report.kill_by_type.head(top_n), use_container_width=True, hide_index=True)
            st.markdown("---")
            st.markdown("""
            **Kill Ratio (KR)** — Probability a defect kills a die.

            | Type | Typical KR |
            |------|-----------|
            | Particle | 0.3–0.5 |
            | Pattern defect | 0.7–1.0 |
            | Scratch | 0.8–1.0 |

            **Poisson model:** Yield = exp(-KR × DD)
            """)
