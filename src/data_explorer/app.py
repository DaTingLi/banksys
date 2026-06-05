"""模块1 · Streamlit 交互式数据探索仪表盘。

启动：streamlit run src/data_explorer/app.py
功能：动态筛选 + Plotly 可视化（分布图 / 相关性热图 / 按 subscribe 分组对比）+ 特征洞察。
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET,
    TRAIN_CSV,
)
from src.data_explorer.insights import (
    feature_insight_report,
    filter_dataframe,
    group_subscribe_rate,
    numeric_correlation,
    overview,
    subscribe_rate,
)


@st.cache_data
def _load() -> pd.DataFrame:
    """加载训练集并缓存，避免每次交互都重读磁盘。"""
    return pd.read_csv(TRAIN_CSV)


def main() -> None:
    """渲染仪表盘主界面。"""
    st.set_page_config(page_title="银行认购数据探索", layout="wide")
    st.title("银行客户认购预测 · 交互式数据探索仪表盘")

    df = _load()

    # 侧边栏：动态筛选。
    st.sidebar.header("动态筛选")
    filters: dict[str, object] = {}
    for col in NUMERIC_FEATURES:
        if col in df.columns:
            low, high = float(df[col].min()), float(df[col].max())
            filters[col] = st.sidebar.slider(col, low, high, (low, high))
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            options = sorted(df[col].dropna().unique().tolist())
            picked = st.sidebar.multiselect(col, options, default=options)
            filters[col] = picked

    filtered = filter_dataframe(df, filters)

    # 顶部指标卡。
    stats = overview(filtered)
    cols = st.columns(4)
    cols[0].metric("样本数", stats.get("行数", 0))
    cols[1].metric("正样本(认购)", stats.get("正样本数", 0))
    cols[2].metric("负样本(未认购)", stats.get("负样本数", 0))
    cols[3].metric("认购率", f"{subscribe_rate(filtered):.1%}")

    # 特征洞察文字报告。
    st.subheader("特征洞察")
    for line in feature_insight_report(filtered, top_categorical="job"):
        st.write("· " + line)

    # 数值分布图。
    st.subheader("数值字段分布")
    num_col = st.selectbox("选择数值字段", list(NUMERIC_FEATURES))
    if num_col in filtered.columns and TARGET in filtered.columns:
        fig = px.histogram(filtered, x=num_col, color=TARGET, barmode="overlay", nbins=40)
        st.plotly_chart(fig, use_container_width=True)

    # 按类别分组的认购率对比。
    st.subheader("按类别看认购率")
    cat_col = st.selectbox("选择类别字段", list(CATEGORICAL_FEATURES))
    grouped = group_subscribe_rate(filtered, cat_col)
    if not grouped.empty:
        fig2 = px.bar(grouped, x=cat_col, y="认购率", hover_data=["样本数"])
        st.plotly_chart(fig2, use_container_width=True)

    # 相关性热图。
    st.subheader("数值字段相关性热图")
    corr = numeric_correlation(filtered, list(NUMERIC_FEATURES))
    if not corr.empty:
        fig3 = px.imshow(corr, text_auto=".2f", aspect="auto")
        st.plotly_chart(fig3, use_container_width=True)


if __name__ == "__main__":
    main()
