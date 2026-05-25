"""YMS Dashboard Module."""
import streamlit as st
from cache_utils import cached_static_query, cached_aggregate_query, cached_list_query, cached_detail_query
from database import run_query
import plotly.express as px
import plotly.graph_objects as go
import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def render():
    """Render the dashboard page."""
    st.title("📊 Yield Management Dashboard")
    
    
    # Top KPI row
    
    c1, c2, c3, c4 = st.columns(4)
    
    
    # Total lots
    
    lots_df = cached_aggregate_query("SELECT COUNT(*) as cnt FROM Lots")
    
    c1.metric("Total Lots", lots_df["cnt"].iloc[0] if not lots_df.empty else 0)
    
    
    # Total measurements
    
    meas_df = cached_aggregate_query("SELECT COUNT(*) as cnt FROM Measurements")
    
    c2.metric("Measurements", meas_df["cnt"].iloc[0] if not meas_df.empty else 0)
    
    
    # Total defects
    
    def_df = cached_aggregate_query("SELECT SUM(Count) as cnt FROM Defects")
    
    c3.metric("Total Defects", int(def_df["cnt"].iloc[0]) if not def_df.empty and not pd.isna(def_df["cnt"].iloc[0]) else 0)
    
    
    # Recent lots with defects
    
    recent_df = cached_list_query("SELECT DISTINCT Lot_ID FROM Defects ORDER BY Lot_ID DESC LIMIT 50")
    
    c4.metric("Affected Lots", len(recent_df))
    
    
    st.markdown("---")
    
    
    # Charts row
    
    col_l, col_r = st.columns(2)
    
    
    with col_l:
    
        st.subheader("📈 Defect Pareto")
    
        pareto_df = cached_aggregate_query("SELECT Defect_Type, SUM(Count) as Total FROM Defects GROUP BY Defect_Type ORDER BY Total DESC LIMIT 10")
    
        if not pareto_df.empty:
    
            fig = px.bar(pareto_df, x="Defect_Type", y="Total", color="Defect_Type",
    
                         title="Top 10 Defect Types")
    
            st.plotly_chart(fig, use_container_width=True)
    
        else:
    
            st.info("No defect data yet. Upload data in 📁 Data Upload page.")
    
    
    with col_r:
    
        st.subheader("📈 Measurement Trends")
    
        params_df = cached_static_query("SELECT DISTINCT Parameter_Name FROM Measurements LIMIT 5")
    
        if not params_df.empty:
    
            param = st.selectbox("Parameter", params_df["Parameter_Name"].tolist())
    
            trend_df = cached_detail_query(
    
                "SELECT Timestamp, Value FROM Measurements WHERE Parameter_Name = ? ORDER BY Timestamp LIMIT 200",
    
                [param],
    
            )
    
            if not trend_df.empty:
    
                trend_df["Timestamp"] = pd.to_datetime(trend_df["Timestamp"])
    
                mean_v = trend_df["Value"].mean()
    
                std_v = trend_df["Value"].std()
    
                fig = go.Figure()
    
                fig.add_trace(go.Scatter(x=trend_df["Timestamp"], y=trend_df["Value"],
    
                                         mode="lines+markers", name=param))
    
                if std_v > 0:
    
                    fig.add_hline(y=mean_v + 3 * std_v, line_dash="dash", line_color="red", annotation_text="UCL")
    
                    fig.add_hline(y=mean_v - 3 * std_v, line_dash="dash", line_color="red", annotation_text="LCL")
    
                fig.update_layout(height=350)
    
                st.plotly_chart(fig, use_container_width=True)
    
        else:
    
            st.info("No measurement data yet.")
    
    
    # Data table
    
    st.markdown("---")
    
    st.subheader("📋 Recent Defect Records")
    
    recent_def = cached_list_query("SELECT * FROM Defects ORDER BY Timestamp DESC LIMIT 20")
    
    if not recent_def.empty:
    
        st.dataframe(recent_def, use_container_width=True)
    
    else:
    
        st.info("No defect records. Upload data to get started.")
    
    
    
    # ═══════════════════════════════════════════════════════════
    
    #  Module 1: Data Upload
    
    # ═══════════════════════════════════════════════════════════
