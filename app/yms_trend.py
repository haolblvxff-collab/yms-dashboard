import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# 页面配置
st.set_page_config(page_title="YMS Dashboard", layout="wide")
st.title("📈 YMS Trend Analysis Module")

# 侧边栏配置
st.sidebar.header("⚙️ Configuration")
param_options = ["Etch Rate (A/min)", "Pressure (mTorr)", "CD (nm)", "Thickness (A)"]
selected_params = st.sidebar.multiselect("Select Parameters", param_options, default=["Etch Rate (A/min)"])
recipe_filter = st.sidebar.selectbox("Recipe Filter", ["All", "ETCH_001", "ETCH_002"])

# 模拟数据生成
@st.cache_data
def generate_data():
    np.random.seed(42)
    dates = pd.date_range(start="2026-04-01", periods=100, freq="H")
    data = {
        "Date": dates,
        "Etch Rate": np.random.normal(1000, 15, 100),
        "Pressure": np.random.normal(50, 0.5, 100),
        "CD": np.random.normal(45, 0.3, 100),
        "Thickness": np.random.normal(5000, 20, 100),
        "Recipe": np.random.choice(["ETCH_001", "ETCH_002"], 100)
    }
    df = pd.DataFrame(data)
    # 模拟 OOC 点
    df.loc[20, "Etch Rate"] = 1060
    df.loc[80, "Pressure"] = 48.0
    return df

df = generate_data()
if recipe_filter != "All":
    df = df[df["Recipe"] == recipe_filter]

# 绘制 Trend Chart
fig = make_subplots(rows=len(selected_params), cols=1, shared_xaxes=True)

for i, param in enumerate(selected_params):
    # 获取 SPC Limits (模拟)
    mean_val = df[param].mean()
    std_val = df[param].std()
    ucl = mean_val + 3 * std_val
    lcl = mean_val - 3 * std_val
    
    # Trace
    fig.add_trace(
        go.Scatter(x=df["Date"], y=df[param], mode='lines+markers', name=param),
        row=i+1, col=1
    )
    
    # SPC Limits
    fig.add_hline(y=ucl, line_dash="dash", line_color="red", annotation_text="UCL", row=i+1, col=1)
    fig.add_hline(y=lcl, line_dash="dash", line_color="red", annotation_text="LCL", row=i+1, col=1)
    fig.add_hline(y=mean_val, line_dash="dot", line_color="green", row=i+1, col=1)

fig.update_layout(height=300 * len(selected_params), title_text="Trend Chart with SPC Limits")
st.plotly_chart(fig, use_container_width=True)

# 数据表格
st.subheader("📊 Raw Data Preview")
st.dataframe(df.head(10))
