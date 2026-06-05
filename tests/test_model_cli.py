"""模块2 入口 CLI 测试：训练落盘 + AUC 门禁退出码。

用小样本写成临时 CSV 并注入，避免依赖全量数据，保证测试快速。
"""

from __future__ import annotations

import pandas as pd

from src import model as model_module


def _prepare(tmp_path, sample_df: pd.DataFrame, monkeypatch):
    """把样本写成临时训练集，并把模型输出指向临时目录。"""
    train_csv = tmp_path / "train.csv"
    sample_df.to_csv(train_csv, index=False)
    model_path = tmp_path / "model.pkl"
    monkeypatch.setattr(model_module, "TRAIN_CSV", train_csv)
    monkeypatch.setattr(model_module, "MODEL_PATH", model_path)
    monkeypatch.setattr(model_module, "MODELS_DIR", tmp_path)
    return model_path


def test_train_saves_model(tmp_path, sample_df, monkeypatch):
    model_path = _prepare(tmp_path, sample_df, monkeypatch)
    best = model_module.train()
    assert model_path.exists()
    assert 0.0 <= best.auc <= 1.0


def test_main_auc_gate_pass(tmp_path, sample_df, monkeypatch):
    _prepare(tmp_path, sample_df, monkeypatch)
    # 阈值 0.0 必然通过，退出码 0
    assert model_module.main(["--check-auc", "0.0"]) == 0


def test_main_auc_gate_fail(tmp_path, sample_df, monkeypatch):
    _prepare(tmp_path, sample_df, monkeypatch)
    # 阈值 0.99 几乎不可能达到，应红灯，退出码 1
    assert model_module.main(["--check-auc", "0.99"]) == 1


def test_main_no_gate_returns_zero(tmp_path, sample_df, monkeypatch):
    _prepare(tmp_path, sample_df, monkeypatch)
    assert model_module.main([]) == 0
