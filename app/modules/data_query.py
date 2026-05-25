"""YMS Data Query Module."""
import streamlit as st
from cache_utils import cached_static_query, cached_aggregate_query, cached_list_query, cached_detail_query
from database import run_query
import pandas as pd

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def render():
    """Render the data_query page."""
    st.title("🔍 Data Query & Explorer")
    
    
    query_mode = st.radio("Mode", ["📋 Table Browser", "💻 SQL Console"], horizontal=True)
    
    
    if query_mode == "📋 Table Browser":
    
        table = st.selectbox("Table", ["Lots", "Measurements", "Defects"])
    
        df = cached_list_query(f"SELECT * FROM {table} LIMIT 200")
    
        st.metric("Row Count (in view)", len(df))
    
    
        # Filters
    
        if table == "Measurements":
    
            col = st.selectbox("Filter by", ["None", "Lot_ID", "Parameter_Name", "Recipe"])
    
            if col != "None":
    
                vals = cached_list_query(f"SELECT DISTINCT {col} FROM {table} LIMIT 50")
    
                selected = st.selectbox(f"Select {col}", vals[col].tolist())
    
                df = cached_detail_query(f"SELECT * FROM {table} WHERE {col} = ? LIMIT 200", [selected])
    
        elif table == "Defects":
    
            col = st.selectbox("Filter by", ["None", "Lot_ID", "Defect_Type", "Severity"])
    
            if col != "None":
    
                vals = cached_list_query(f"SELECT DISTINCT {col} FROM {table} LIMIT 50")
    
                selected = st.selectbox(f"Select {col}", vals[col].tolist())
    
                df = cached_detail_query(f"SELECT * FROM {table} WHERE {col} = ? LIMIT 200", [selected])
    
    
        st.dataframe(df, use_container_width=True)
    
    
        # Download
    
        if not df.empty:
    
            csv = df.to_csv(index=False)
    
            st.download_button("📥 Download CSV", csv, f"{table}_export.csv", "text/csv")
    
    
    else:
    
        st.subheader("💻 SQL Console (Read-Only)")
    
        st.caption("Available tables: `Lots`, `Measurements`, `Defects`, `DOE_Experiments`")
    
    
        examples = st.selectbox("Quick examples", [
    
            "Custom query...",
    
            "SELECT Defect_Type, SUM(Count) as Total FROM Defects GROUP BY Defect_Type ORDER BY Total DESC",
    
            "SELECT Lot_ID, COUNT(*) as records FROM Measurements GROUP BY Lot_ID",
    
            "SELECT * FROM Defects WHERE Severity = 'Critical'",
    
        ])
    
    
        sql = st.text_area("SQL Query",
    
                           value=examples if examples != "Custom query..." else "SELECT * FROM Measurements LIMIT 20",
    
                           height=100)
    
    
        if st.button("▶️ Execute"):
    
            try:
    
                df = run_query(sql)
    
                st.success(f"{len(df)} rows returned")
    
                st.dataframe(df, use_container_width=True)
    
                if not df.empty:
    
                    csv = df.to_csv(index=False)
    
                    st.download_button("📥 Download Results", csv, "query_result.csv", "text/csv")
    
            except Exception as e:
    
                st.error(f"Query error: {e}")
    
    
    
    # ═══════════════════════════════════════════════════════════
    
    #  Module 3: SPC Analysis (Enhanced)
    
    # ═══════════════════════════════════════════════════════════
