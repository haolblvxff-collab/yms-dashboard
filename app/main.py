"""
YMS Web Dashboard v2.0 — Streamlit frontend (modularized).
"""
import streamlit as st
import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, run_query, get_connection, insert_query
from cache_utils import (
    cached_static_query, cached_aggregate_query,
    cached_list_query, cached_detail_query,
)

st.set_page_config(page_title="YMS Dashboard v2.0", layout="wide", page_icon="🏭")

# ─── Init DB ───────────────────────────────────────────────
init_db()

# ─── Sidebar Navigation ────────────────────────────────────
st.sidebar.title("🏭 YMS v2.0")
page = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "📁 Data Upload",
    "🔍 Data Query",
    "📈 SPC Analysis",
    "🗺️ Wafer Map",
    "📅 Lot Gantt",
    "🧪 DOE",
    "🔬 MSA/GR&R",
    "🔗 Correlation",
    "📉 Yield Analysis",
    "📋 Process Flow",
])

st.sidebar.markdown("---")
st.sidebar.caption(f"DB: `yms_data.db` | {datetime.date.today()}")


# ═══════════════════════════════════════════════════════════
#  Module Router
# ═══════════════════════════════════════════════════════════

if page == "📊 Dashboard":
    from modules.dashboard import render
    render()

elif page == "📁 Data Upload":
    from modules.data_upload import render
    render()

elif page == "🔍 Data Query":
    from modules.data_query import render
    render()

elif page == "📈 SPC Analysis":
    from modules.spc_analysis import render
    render()

elif page == "🗺️ Wafer Map":
    from modules.wafer_map import render
    render()

elif page == "📅 Lot Gantt":
    from modules.lot_gantt import render
    render()

elif page == "🧪 DOE":
    from yms_doe_enhanced import render_doe_page
    render_doe_page(db_run_query=run_query, db_insert_query=insert_query)

elif page == "🔬 MSA/GR&R":
    from yms_msa import render_msa_page
    render_msa_page(db_run_query=run_query, db_insert_query=insert_query)

elif page == "🔗 Correlation":
    from yms_correlation import render_correlation_page
    render_correlation_page(db_run_query=run_query)

elif page == "📉 Yield Analysis":
    from yms_yield import render_yield_page
    render_yield_page(db_run_query=run_query)

elif page == "📋 Process Flow":
    from yms_process_flow import render_process_flow_page
    render_process_flow_page(db_run_query=run_query)
