"""模块2 · 训练流程单元测试（用小样本，跑得快）。"""

from __future__ import annotations

import pandas as pd
import pytest

from src.config import FEATURE_COLUMNS
from src.model_training.pipeline import (
    build_preprocessor,
    prepare_xy,
    train_and_select,
)


def test_prepare_xy_drops_leakage_and_id(sample_df: pd.DataFrame):
    x, y = prepare_xy(sample_df)
    # 入模特征不应包含 id / duration / subscribe
    assert "duration" not in x.columns
    assert "id" not in x.columns
    assert "subscribe" not in x.columns
    assert list(x.columns) == list(FEATURE_COLUMNS)
    # 标签是 0/1
    assert set(y.unique()).issubset({0, 1})


def test_prepare_xy_without_target_raises():
    df = pd.DataFrame({"age": [1, 2], "job": ["a", "b"]})
    with pytest.raises(ValueError):
        prepare_xy(df)


def test_preprocessor_builds():
    pre = build_preprocessor()
    assert pre is not None


def test_train_and_select_returns_valid_auc(sample_df: pd.DataFrame):
    best, results = train_and_select(sample_df)
    assert len(results) == 3
    # AUC 必须是合法概率指标
    assert 0.0 <= best.auc <= 1.0
    # 小样本也应明显优于随机(0.5)
    assert best.auc > 0.6
    # 最佳模型确实是 AUC 最高者
    assert best.auc == max(r.auc for r in results)
