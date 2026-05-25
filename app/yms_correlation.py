"""
YMS Correlation Analysis — Streamlit UI
========================================
Parameter-to-parameter and parameter-to-yield correlation.
Pearson / Spearman, heatmap, scatter plots, key parameter ranking.
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import importlib.util

# ── Import engine ──
_eng_path = os.path.join(os.path.dirname(__file__), "..", "src", "yms", "analysis", "correlation_engine.py")
_spec = importlib.util.spec_from_file_location("correlation_engine", os.path.abspath(_eng_path))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CorrelationAnalysis = _mod.CorrelationAnalysis

corr_eng = CorrelationAnalysis()


def render_correlation_page(db_run_query=None):
    """Render correlation analysis Streamlit page."""
    st.title("🔗 Correlation Analysis")
    st.caption("Process parameter correlation · Pearson & Spearman")

    if db_run_query is None:
        st.error("Database connection not available.")
        return

    # ── Data Source ──
    st.markdown("### 📂 Data Source")
    src_col1, src_col2 = st.columns(2)
    with src_col1:
        data_source = st.radio("Source", ["📊 Database (Measurements)", "📁 Upload CSV"],
                                horizontal=True)

    df = None
    numeric_cols = []
    yield_col = None

    if data_source == "📊 Database (Measurements)":
        # Pivot measurements into wide format (one column per parameter)
        raw = db_run_query("SELECT Lot_ID, Parameter_Name, AVG(Value) as Mean_Value FROM Measurements GROUP BY Lot_ID, Parameter_Name ORDER BY Lot_ID")
        if raw.empty:
            st.warning("No measurement data in database.")
            return
        df = raw.pivot(index="Lot_ID", columns="Parameter_Name", values="Mean_Value").reset_index()
        # Add yield: from lot completion status (simplified)
        lots = db_run_query("SELECT Lot_ID, Yield FROM Lots")
        if not lots.empty:
            df = df.merge(lots[["Lot_ID", "Yield"]], on="Lot_ID", how="left")
            df["Yield"] = df["Yield"].fillna(0.85)

        numeric_cols = [c for c in df.columns if c not in ("Lot_ID",) and df[c].dtype in ("float64", "int64")]
        yield_candidates = ["Yield", "yield_rate"]
        for yc in yield_candidates:
            if yc in df.columns:
                yield_col = yc
                break
        if yield_col is None and len(numeric_cols) > 1:
            yield_col = numeric_cols[-1]  # Last column as fallback

        with src_col2:
            st.metric("Lots", len(df))
            st.metric("Parameters", len(numeric_cols) - 1)
            st.metric("Yield Column", yield_col or "N/A")

    else:
        uploaded = st.file_uploader("Upload CSV", type=["csv"],
                                     help="Columns: parameter columns + yield column")
        if uploaded:
            df = pd.read_csv(uploaded)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                yield_col = st.selectbox("Select Yield Column", numeric_cols,
                                          index=len(numeric_cols) - 1)
            st.metric("Rows", len(df))
            st.metric("Numeric Columns", len(numeric_cols))

    if df is None or len(numeric_cols) < 2:
        st.info("Need at least 2 numeric columns for correlation analysis.")
        return

    param_cols = [c for c in numeric_cols if c != yield_col]

    # ── Analysis Controls ──
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        method = st.selectbox("Correlation Method", ["spearman", "pearson"],
                               help="Spearman: rank-based, robust to outliers (recommended for semi data). "
                                    "Pearson: linear, assumes normality.")
    with c2:
        min_corr = st.slider("Min |r| for Key Params", 0.1, 0.7, 0.3, 0.05)
    with c3:
        max_p = st.selectbox("Significance Level", [0.05, 0.01, 0.001],
                              format_func=lambda x: f"p < {x}")

    if not st.button("▶️ Run Correlation Analysis", use_container_width=True):
        st.info("Configure parameters above and click Run.")
        return

    # ── Run Analysis ──
    ranking = corr_eng.analyze(df, param_cols, yield_col, method=method)
    corr_matrix = corr_eng.cross_correlation_matrix(df, param_cols + [yield_col], method=method)
    key_params = corr_eng.find_key_params(ranking, min_corr=min_corr, max_p=max_p)

    # ── Results Display ──
    st.markdown("---")
    st.markdown("### 📊 Results")

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Method", method.capitalize())
    with k2:
        st.metric("Parameters Analyzed", len(param_cols))
    with k3:
        n_key = len(key_params)
        st.metric("Key Parameters Found", n_key, delta=f"|r|≥{min_corr}" if n_key > 0 else None)
    with k4:
        top_param = ranking.iloc[0] if not ranking.empty else None
        if top_param is not None:
            st.metric("Top Correlated", f"{top_param['Parameter']}",
                      delta=f"r={top_param['Correlation']:.3f}")

    # ── Charts ──
    tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "📊 Ranking", "🔍 Scatter Detail"])

    with tab1:
        st.plotly_chart(corr_eng.build_heatmap(corr_matrix,
                          title=f"{method.capitalize()} Correlation Heatmap"),
                        use_container_width=True)

    with tab2:
        col_a, col_b = st.columns([3, 2])
        with col_a:
            st.plotly_chart(corr_eng.build_ranking_bar(ranking), use_container_width=True)
        with col_b:
            st.markdown("#### Ranking Table")
            disp_cols = ["Parameter", "Correlation", "P_value", "Significance"]
            display = ranking[disp_cols].copy()
            display["Correlation"] = display["Correlation"].round(4)
            display["P_value"] = display["P_value"].apply(lambda p: f"{p:.4f}")
            st.dataframe(display, use_container_width=True, hide_index=True, height=400)

            if len(key_params) > 0:
                st.markdown(f"#### 🔑 Key Parameters (|r|≥{min_corr}, p<{max_p})")
                st.dataframe(key_params[disp_cols], use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("#### Scatter Plots — Top Correlations")
        top_n = st.slider("Show top N", 2, min(12, len(ranking)), 6, key="scatter_n")
        top_params = ranking.head(top_n)["Parameter"].tolist()
        for param in top_params:
            st.plotly_chart(corr_eng.build_scatter_pair(df, param, yield_col, method=method),
                            use_container_width=True)
