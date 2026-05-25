"""Cache utility functions for YMS Streamlit dashboard."""
import streamlit as st
from database import run_query

# ═══ Cache Utilities ═══
# TTL tiers: STATIC=600s, AGGREGATE=300s, LIST=120s, DETAIL=60s

@st.cache_data(ttl=600, show_spinner=False)
def cached_static_query(sql):
    """静态数据：参数列表、产品列表（10分钟）"""
    return run_query(sql)

@st.cache_data(ttl=300, show_spinner=False)
def cached_aggregate_query(sql):
    """聚合数据：COUNT/SUM/GROUP BY（5分钟）"""
    return run_query(sql)

@st.cache_data(ttl=120, show_spinner=False)
def cached_list_query(sql, params=None):
    """列表数据：最近记录、缺陷列表（2分钟）"""
    return run_query(sql, params or [])

@st.cache_data(ttl=60, show_spinner=False)
def cached_detail_query(sql, params=None):
    """详情数据：单参数/单Lot过滤（1分钟）"""
    return run_query(sql, params or [])


