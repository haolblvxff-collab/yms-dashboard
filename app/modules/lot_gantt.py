"""YMS Lot Gantt Module."""
import streamlit as st
from cache_utils import cached_static_query, cached_aggregate_query, cached_list_query, cached_detail_query
from database import run_query
import plotly.express as px
import pandas as pd

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def render():
    """Render the lot_gantt page."""
    st.title("📅 Lot Tracking Gantt")
    
    
    lots_df = cached_list_query("SELECT Lot_ID FROM Lots ORDER BY Lot_ID DESC LIMIT 50")
    
    lot_list = lots_df["Lot_ID"].tolist() if not lots_df.empty else []
    
    lot_id = st.selectbox("Lot ID", lot_list) if lot_list else st.text_input("Lot ID", "LOT-2026-001")
    
    
    if lot_id:
    
        meas = cached_detail_query("SELECT * FROM Measurements WHERE Lot_ID = ? ORDER BY Timestamp", [lot_id])
    
        if not meas.empty:
    
            meas["Timestamp"] = pd.to_datetime(meas["Timestamp"])
    
            steps = meas["Parameter_Name"].unique()
    
    
            data = []
    
            base = meas["Timestamp"].min()
    
            for step in steps:
    
                step_data = meas[meas["Parameter_Name"] == step]
    
                start = step_data["Timestamp"].min()
    
                end = step_data["Timestamp"].max()
    
                data.append({"Step": step, "Start": start, "End": end})
    
    
            if data:
    
                gantt_df = pd.DataFrame(data)
    
                fig = px.timeline(gantt_df, x_start="Start", x_end="End", y="Step", color="Step",
    
                                  title=f"Lot {lot_id} — Process Flow")
    
                fig.update_yaxes(autorange="reversed")
    
                fig.update_layout(height=350)
    
                st.plotly_chart(fig, use_container_width=True)
    
    
            st.subheader("Step Details")
    
            detail = meas.groupby("Parameter_Name").agg(
    
                Count=("Value", "count"),
    
                Mean=("Value", "mean"),
    
                Min=("Value", "min"),
    
                Max=("Value", "max"),
    
                Std=("Value", "std"),
    
            ).reset_index()
    
            st.dataframe(detail, use_container_width=True)
    
        else:
    
            st.info(f"No measurement data for Lot {lot_id}")
