"""数据洞察纯函数层。

把“算什么”与“怎么展示”分离：本文件只做可测试的纯计算，
Streamlit 页面（app.py）只负责调用这些函数并渲染，方便单元测试覆盖。
"""

from __future__ import annotations

import pandas as pd

from src.config import POSITIVE_LABEL, TARGET


def overview(df: pd.DataFrame) -> dict[str, int]:
    """返回样本量、特征数、正/负样本数等总览指标。"""
    n_rows, n_cols = df.shape
    result = {"行数": int(n_rows), "列数": int(n_cols)}
    if TARGET in df.columns:
        counts = df[TARGET].value_counts()
        result["正样本数"] = int(counts.get(POSITIVE_LABEL, 0))
        result["负样本数"] = int(n_rows - counts.get(POSITIVE_LABEL, 0))
    return result


def subscribe_rate(df: pd.DataFrame) -> float:
    """计算整体认购率（正样本占比），无目标列时返回 0.0。"""
    if TARGET not in df.columns or len(df) == 0:
        return 0.0
    return float((df[TARGET] == POSITIVE_LABEL).mean())


def filter_dataframe(df: pd.DataFrame, filters: dict[str, object]) -> pd.DataFrame:
    """按字段做动态筛选。

    filters 支持两种取值：
    - 区间元组 (low, high)：用于数值字段，闭区间过滤。
    - 取值列表 [...]：用于类别字段，做 isin 过滤。
    空列表或 None 表示该字段不过滤。
    """
    mask = pd.Series(True, index=df.index)
    for column, condition in filters.items():
        if condition is None or column not in df.columns:
            continue
        if isinstance(condition, tuple) and len(condition) == 2:
            low, high = condition
            mask &= df[column].between(low, high)
        elif isinstance(condition, list | set):
            values = list(condition)
            if values:
                mask &= df[column].isin(values)
    return df[mask]


def group_subscribe_rate(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """按某个类别字段分组统计认购率，按认购率降序返回。"""
    if by not in df.columns or TARGET not in df.columns:
        return pd.DataFrame(columns=[by, "认购率", "样本数"])
    grouped = (
        df.assign(_pos=(df[TARGET] == POSITIVE_LABEL).astype(int))
        .groupby(by)
        .agg(认购率=("_pos", "mean"), 样本数=("_pos", "size"))
        .reset_index()
        .sort_values("认购率", ascending=False)
    )
    return grouped


def numeric_correlation(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    """计算数值字段间的相关系数矩阵（用于热力图）。"""
    present = [c for c in numeric_columns if c in df.columns]
    if not present:
        return pd.DataFrame()
    return df[present].corr(numeric_only=True)


def feature_insight_report(df: pd.DataFrame, top_categorical: str) -> list[str]:
    """生成一份简短的特征洞察文字报告。"""
    lines: list[str] = []
    rate = subscribe_rate(df)
    lines.append(f"整体认购率：{rate:.1%}")
    if top_categorical in df.columns and TARGET in df.columns:
        grouped = group_subscribe_rate(df, top_categorical)
        if not grouped.empty:
            best = grouped.iloc[0]
            lines.append(
                f"按「{top_categorical}」看，认购率最高的是 "
                f"{best[top_categorical]}（{best['认购率']:.1%}）"
            )
    return lines
