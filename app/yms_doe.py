import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from itertools import product
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# 页面配置
st.set_page_config(page_title="YMS DOE System", layout="wide")
st.title("🧪 DOE Data Analysis System")

# 侧边栏
st.sidebar.header("📝 Experiment Design")
num_factors = st.sidebar.slider("Number of Factors", 2, 4, 2)

# 模拟 DOE 数据
@st.cache_data
def generate_doe_data(factors):
    np.random.seed(42)
    levels = [-1, 1]
    
    # 创建全因子设计
    design = list(product(levels, repeat=factors))
    df = pd.DataFrame(design, columns=[f"Factor_{i+1}" for i in range(factors)])
    
    # 模拟响应值 (带有交互作用)
    y = 50 + 10 * df["Factor_1"] + 5 * df["Factor_2"] + 8 * df["Factor_1"] * df["Factor_2"]
    y += np.random.normal(0, 1, len(df))
    df["Response"] = y
    
    return df

factors_df = generate_doe_data(num_factors)
factor_names = [col for col in factors_df.columns if col != "Response"]

# 选项卡
tab1, tab2, tab3 = st.tabs(["📊 Main Effects", "🕸️ Interaction Plot", "📋 Raw Data"])

with tab1:
    st.subheader("Main Effects Plot")
    # 计算 Main Effects
    means = factors_df.groupby(factor_names).mean().reset_index()
    
    fig, axes = plt.subplots(1, len(factor_names), figsize=(15, 5))
    if len(factor_names) == 1: axes = [axes]
    
    for i, factor in enumerate(factor_names):
        effect_means = factors_df.groupby(factor)["Response"].mean()
        axes[i].bar([-1, 1], effect_means.values, color=['blue', 'orange'])
        axes[i].set_xticks([-1, 1])
        axes[i].set_xticklabels(["Low", "High"])
        axes[i].set_title(factor)
        axes[i].set_ylabel("Mean Response")
        
    st.pyplot(fig)

with tab2:
    st.subheader("Interaction Plot")
    if len(factor_names) >= 2:
        f1, f2 = factor_names[0], factor_names[1]
        interaction_means = factors_df.groupby([f1, f2])["Response"].mean().reset_index()
        
        fig = px.line(
            interaction_means, x=f2, y="Response", color=f1.astype(str),
            markers=True, title=f"Interaction: {f1} x {f2}"
        )
        fig.update_xaxes(tickvals=[-1, 1], ticktext=["Low", "High"])
        st.plotly_chart(fig, use_container_width=True)
        
        # ANOVA 提示
        st.info("💡 Parallel lines indicate no interaction. Crossing lines indicate significant interaction.")

with tab3:
    st.subheader("Experiment Raw Data")
    st.dataframe(factors_df)
    
    # 简单的回归分析
    st.subheader("📈 Regression Analysis Summary")
    X = factors_df[factor_names]
    y = factors_df["Response"]
    model = LinearRegression().fit(X, y)
    
    st.write(f"**R² Score**: {model.score(X, y):.4f}")
    
    coeff_df = pd.DataFrame({
        "Factor": ["Intercept"] + factor_names,
        "Coefficient": [model.intercept_] + list(model.coef_)
    })
    st.table(coeff_df)
