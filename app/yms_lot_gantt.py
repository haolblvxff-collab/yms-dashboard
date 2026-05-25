import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import numpy as np

# 页面配置
st.set_page_config(page_title="YMS Lot Tracking", layout="wide")
st.title("📅 Lot Gantt Chart (Lot Tracking)")

# 侧边栏
st.sidebar.header("🔍 Lot Search")
lot_id = st.sidebar.text_input("Enter Lot ID", value="LOT-2026-001")

# 模拟 Lot 流转数据
@st.cache_data
def generate_lot_data(lot_id):
    np.random.seed(hash(lot_id) % 2**32)
    steps = ["Oxidation", "Lithography", "Etch", "Deposition", "CMP", "Metrology"]
    
    # 基础时间设置
    base_time = datetime.datetime(2026, 4, 20, 8, 0, 0)
    current_time = base_time
    
    data = []
    for i, step in enumerate(steps):
        # Process Time (1-4 hours)
        process_time = pd.Timedelta(hours=np.random.uniform(1, 4))
        start = current_time
        
        # Wait Time (0-2 hours, sometimes high for bottleneck)
        wait_time = pd.Timedelta(hours=np.random.uniform(0, 2))
        if i == 3: # Simulate bottleneck at Deposition
            wait_time += pd.Timedelta(hours=5)
            
        end = start + process_time + wait_time
        
        data.append({
            "Step": step,
            "Start Time": start,
            "End Time": end,
            "Process Time": process_time,
            "Wait Time": wait_time,
            "Status": "Completed" if end < datetime.datetime.now() else "In Progress"
        })
        
        current_time = end + pd.Timedelta(minutes=np.random.uniform(15, 60))
        
    return pd.DataFrame(data)

df = generate_lot_data(lot_id)

# 数据转换用于 Plotly Gantt
df_gantt = df.copy()
df_gantt["Step"] = pd.Categorical(df_gantt["Step"], categories=df_gantt["Step"][::-1], ordered=True)

# 绘制 Gantt Chart
fig = px.timeline(
    df_gantt, 
    x_start="Start Time", 
    x_end="End Time", 
    y="Step",
    color="Step",
    hover_data=["Process Time", "Wait Time", "Status"],
    title=f"Lot Tracking: {lot_id}"
)

# 添加 Wait Time 标记 (红色区块)
for i, row in df.iterrows():
    if row["Wait Time"].total_seconds() > 3600: # > 1 hour
        fig.add_vrect(
            x0=row["Start Time"] + row["Process Time"],
            x1=row["End Time"],
            fillcolor="red", opacity=0.3, layer="below", line_width=0
        )

fig.update_yaxes(autorange="reversed") # Reverse Y axis to show flow top-to-bottom
fig.update_layout(height=400)

st.plotly_chart(fig, use_container_width=True)

# 关键指标
col1, col2, col3 = st.columns(3)
total_process = df["Process Time"].sum()
total_wait = df["Wait Time"].sum()
q_time_violations = len(df[df["Wait Time"] > pd.Timedelta(hours=4)])

col1.metric("Total Cycle Time", f"{total_process + total_wait}")
col2.metric("Process Time", f"{total_process}")
col3.metric("Q-Time Violations", q_time_violations, delta_color="inverse")

# 明细表
st.subheader("📋 Step-by-Step Details")
st.dataframe(df.drop(columns=["Start Time", "End Time"]))
