"""YMS Data Upload Module."""
import streamlit as st
from cache_utils import cached_static_query, cached_aggregate_query, cached_list_query, cached_detail_query
from database import run_query
import io
import pandas as pd

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def render():
    """Render the data_upload page."""
    st.title("📁 Data Upload & Import")
    
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload File", "📥 Download Template", "✏️ Manual Entry"])
    
    
    with tab1:
    
        st.subheader("Upload CSV / Excel")
    
        st.markdown("""
    
        Supported formats: `.csv`, `.xlsx`
    
    
        **Expected columns** (auto-detected):
    
        - **Measurements**: `Lot_ID, Timestamp, Parameter_Name, Value, Recipe`
    
        - **Defects**: `Lot_ID, Wafer_ID, Defect_Type, Count, Severity, Timestamp`
    
        - **Lots**: `Lot_ID, Product_ID, Start_Time, End_Time, Status`
    
        """)
    
    
        uploaded = st.file_uploader("Choose files", type=["csv", "xlsx"], accept_multiple_files=True)
    
    
        if uploaded:
    
            for f in uploaded:
    
                try:
    
                    ext = f.name.split(".")[-1].lower()
    
                    if ext == "csv":
    
                        df = pd.read_csv(f)
    
                    else:
    
                        df = pd.read_excel(f)
    
    
                    st.write(f"**{f.name}** — {len(df)} rows, {len(df.columns)} columns")
    
                    st.dataframe(df.head(5))
    
    
                    # Detect table
    
                    from api import _detect_table, _import_dataframe
    
                    cols_lower = [c.lower().strip() for c in df.columns]
    
                    table = _detect_table(cols_lower)
    
                    if table:
    
                        if st.button(f"✅ Import to **{table}**", key=f"btn_{f.name}"):
    
                            count = _import_dataframe(df, table)
    
                            st.success(f"Imported {count} rows into {table}!")
    
                            st.cache_data.clear()
    
                            st.rerun()
    
                    else:
    
                        st.warning(f"Cannot detect table type. Columns: {list(df.columns)}")
    
                except Exception as e:
    
                    st.error(f"Error reading {f.name}: {e}")
    
    
    with tab2:
    
        st.subheader("Download CSV Templates")
    
        c1, c2, c3 = st.columns(3)
    
        with c1:
    
            st.download_button("📥 Measurements Template",
    
                               data="Lot_ID,Timestamp,Parameter_Name,Value,Recipe\nLOT-001,2026-05-01T08:00:00,Etch Rate,1000,ETCH_001\n",
    
                               file_name="yms_measurements_template.csv", mime="text/csv")
    
        with c2:
    
            st.download_button("📥 Defects Template",
    
                               data="Lot_ID,Wafer_ID,Defect_Type,Count,Severity,Timestamp\nLOT-001,W01,Particle,5,Medium,2026-05-01T08:00:00\n",
    
                               file_name="yms_defects_template.csv", mime="text/csv")
    
        with c3:
    
            st.download_button("📥 Lots Template",
    
                               data="Lot_ID,Product_ID,Start_Time,End_Time,Status\nLOT-001,DEVICE-A,2026-05-01T08:00:00,2026-05-02T08:00:00,Completed\n",
    
                               file_name="yms_lots_template.csv", mime="text/csv")
    
    
    with tab3:
    
        st.subheader("Manual Data Entry")
    
        entry_type = st.selectbox("Table", ["Measurements", "Defects", "Lots"])
    
    
        if entry_type == "Measurements":
    
            with st.form("manual_meas"):
    
                lot = st.text_input("Lot ID", "LOT-MANUAL-001")
    
                param = st.text_input("Parameter Name", "CD")
    
                val = st.number_input("Value", value=45.0)
    
                recipe = st.text_input("Recipe", "ETCH_001")
    
                if st.form_submit_button("Add"):
    
                    get_connection().execute(
    
                        "INSERT INTO Measurements (Lot_ID, Timestamp, Parameter_Name, Value, Recipe) VALUES (?,?,?,?,?)",
    
                        [lot, datetime.datetime.now().isoformat(), param, val, recipe],
    
                    ).connection.commit() if False else None
    
                    conn = get_connection()
    
                    conn.execute(
    
                        "INSERT INTO Measurements (Lot_ID, Timestamp, Parameter_Name, Value, Recipe) VALUES (?,?,?,?,?)",
    
                        [lot, datetime.datetime.now().isoformat(), param, val, recipe],
    
                    )
    
                    conn.commit()
    
                    conn.close()
    
                    st.success("Added!")
    
                    st.rerun()
    
    
        elif entry_type == "Defects":
    
            with st.form("manual_defect"):
    
                lot = st.text_input("Lot ID", "LOT-MANUAL-001")
    
                wafer = st.text_input("Wafer ID", "W01")
    
                dtype = st.selectbox("Defect Type", ["Particle", "Scratch", "Pattern", "Void", "Residue", "Other"])
    
                cnt = st.number_input("Count", min_value=1, value=1)
    
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    
                if st.form_submit_button("Add"):
    
                    conn = get_connection()
    
                    conn.execute(
    
                        "INSERT INTO Defects (Lot_ID, Wafer_ID, Defect_Type, Count, Severity, Timestamp) VALUES (?,?,?,?,?,?)",
    
                        [lot, wafer, dtype, cnt, severity, datetime.datetime.now().isoformat()],
    
                    )
    
                    conn.commit()
    
                    conn.close()
    
                    st.success("Added!")
    
                    st.rerun()
    
    
        elif entry_type == "Lots":
    
            with st.form("manual_lot"):
    
                lot = st.text_input("Lot ID", "LOT-MANUAL-001")
    
                product = st.text_input("Product ID", "DEVICE-A")
    
                status = st.selectbox("Status", ["In Progress", "Completed", "On Hold", "Scrapped"])
    
                if st.form_submit_button("Add"):
    
                    conn = get_connection()
    
                    conn.execute(
    
                        "INSERT OR REPLACE INTO Lots (Lot_ID, Product_ID, Status) VALUES (?,?,?)",
    
                        [lot, product, status],
    
                    )
    
                    conn.commit()
    
                    conn.close()
    
                    st.success("Added!")
    
                    st.rerun()
    
    
    
    # ═══════════════════════════════════════════════════════════
    
    #  Module 2: Data Query
    
    # ═══════════════════════════════════════════════════════════
