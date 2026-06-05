"""模块1 · 数据洞察纯函数单元测试。"""

from __future__ import annotations

import pandas as pd

from src.data_explorer.insights import (
    feature_insight_report,
    filter_dataframe,
    group_subscribe_rate,
    numeric_correlation,
    overview,
    subscribe_rate,
)


def _toy() -> pd.DataFrame:
    """构造一个可手算的小数据集。"""
    return pd.DataFrame(
        {
            "age": [25, 35, 45, 55],
            "job": ["admin.", "admin.", "blue-collar", "blue-collar"],
            "campaign": [1, 2, 3, 4],
            "subscribe": ["yes", "no", "yes", "no"],
        }
    )


def test_overview_counts_rows_and_labels():
    df = _toy()
    stats = overview(df)
    assert stats["行数"] == 4
    assert stats["正样本数"] == 2
    assert stats["负样本数"] == 2


def test_subscribe_rate_is_half():
    assert subscribe_rate(_toy()) == 0.5


def test_subscribe_rate_empty_returns_zero():
    assert subscribe_rate(pd.DataFrame()) == 0.0


def test_filter_numeric_range():
    df = _toy()
    filtered = filter_dataframe(df, {"age": (30, 50)})
    assert filtered["age"].tolist() == [35, 45]


def test_filter_categorical_list():
    df = _toy()
    filtered = filter_dataframe(df, {"job": ["admin."]})
    assert len(filtered) == 2
    assert set(filtered["job"]) == {"admin."}


def test_filter_ignores_none_and_missing_column():
    df = _toy()
    filtered = filter_dataframe(df, {"age": None, "not_exist": ["x"]})
    assert len(filtered) == 4


def test_group_subscribe_rate_sorted_desc():
    df = _toy()
    grouped = group_subscribe_rate(df, "job")
    assert list(grouped.columns) == ["job", "认购率", "样本数"]
    assert grouped.iloc[0]["认购率"] >= grouped.iloc[-1]["认购率"]


def test_numeric_correlation_shape():
    df = _toy()
    corr = numeric_correlation(df, ["age", "campaign"])
    assert corr.shape == (2, 2)


def test_numeric_correlation_empty_when_no_columns():
    corr = numeric_correlation(_toy(), ["not_exist"])
    assert corr.empty


def test_feature_insight_report_has_rate_line():
    lines = feature_insight_report(_toy(), top_categorical="job")
    assert any("认购率" in line for line in lines)
