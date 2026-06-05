"""模块3 · FastAPI 在线预测服务测试。

用小样本现场训练一个 pipeline 注入服务，避免依赖已落盘的 models/model.pkl。
"""

from __future__ import annotations

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.model_training.pipeline import build_preprocessor, prepare_xy
from src.prediction_service import service
from src.prediction_service.service import app

_EXAMPLE = {
    "job": "admin.",
    "marital": "married",
    "education": "university.degree",
    "default": "no",
    "housing": "yes",
    "loan": "no",
    "contact": "cellular",
    "month": "may",
    "day_of_week": "mon",
    "poutcome": "nonexistent",
    "age": 41,
    "campaign": 2,
    "pdays": 999,
    "previous": 0,
    "emp_var_rate": -1.8,
    "cons_price_index": 92.89,
    "cons_conf_index": -46.2,
    "lending_rate3m": 1.31,
    "nr_employed": 5099.1,
}


@pytest.fixture(autouse=True)
def _inject_model(sample_df: pd.DataFrame):
    """训练一个轻量模型并注入服务全局缓存。"""
    x, y = prepare_xy(sample_df)
    pipe = Pipeline(
        steps=[("prep", build_preprocessor()), ("clf", LogisticRegression(max_iter=500))]
    )
    pipe.fit(x, y)
    service._model = pipe
    yield
    service._model = None


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_ok(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_predict_single(client: TestClient):
    resp = client.post("/predict", json=_EXAMPLE)
    assert resp.status_code == 200
    body = resp.json()
    assert body["subscribe"] in {"yes", "no"}
    assert 0.0 <= body["probability"] <= 1.0
    assert body["confidence"] in {"high", "medium", "low"}


def test_predict_batch(client: TestClient):
    resp = client.post("/predict/batch", json={"customers": [_EXAMPLE, _EXAMPLE]})
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 2


def test_predict_batch_empty_rejected(client: TestClient):
    resp = client.post("/predict/batch", json={"customers": []})
    assert resp.status_code == 400


def test_predict_missing_field_422(client: TestClient):
    bad = dict(_EXAMPLE)
    del bad["age"]
    resp = client.post("/predict", json=bad)
    assert resp.status_code == 422
