"""模块3 · FastAPI 在线预测服务。

启动：uvicorn src.prediction_service.service:app --host 0.0.0.0 --port 8000
接口：
- GET  /health          健康检查（CD 部署后校验用）
- POST /predict         单条预测
- POST /predict/batch   批量预测
- GET  /docs            Swagger 在线调试
"""

from __future__ import annotations

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from src.config import FEATURE_COLUMNS, MODEL_PATH, POSITIVE_LABEL, SERVICE_PORT
from src.prediction_service.schemas import (
    BatchRequest,
    BatchResponse,
    Customer,
    PredictionResult,
)

app = FastAPI(title="银行客户认购预测服务", version="1.0.0")

# 进程级模型缓存：首个请求时懒加载，避免无模型时导入即崩。
_model = None


def _load_model():
    """懒加载 models/model.pkl。"""
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise HTTPException(
                status_code=503,
                detail="模型尚未训练。请先运行 python -m src.model 生成 models/model.pkl。",
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def _confidence(prob: float) -> str:
    """根据概率与 0.5 的距离给出置信度档位。"""
    margin = abs(prob - 0.5)
    if margin >= 0.3:
        return "high"
    if margin >= 0.15:
        return "medium"
    return "low"


def _predict_frame(df: pd.DataFrame) -> list[PredictionResult]:
    """对一批客户做预测，返回结果列表。"""
    model = _load_model()
    probs = model.predict_proba(df[list(FEATURE_COLUMNS)])[:, 1]
    results: list[PredictionResult] = []
    for prob in probs:
        label = POSITIVE_LABEL if prob >= 0.5 else "no"
        results.append(
            PredictionResult(
                subscribe=label,
                probability=round(float(prob), 4),
                confidence=_confidence(float(prob)),
            )
        )
    return results


@app.get("/health")
def health() -> dict[str, str]:
    """健康检查：仅表示进程存活，不强制要求模型已加载。"""
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResult)
def predict(customer: Customer) -> PredictionResult:
    """单条预测。"""
    df = pd.DataFrame([customer.model_dump()])
    return _predict_frame(df)[0]


@app.post("/predict/batch", response_model=BatchResponse)
def predict_batch(req: BatchRequest) -> BatchResponse:
    """批量预测。"""
    if not req.customers:
        raise HTTPException(status_code=400, detail="customers 不能为空。")
    df = pd.DataFrame([c.model_dump() for c in req.customers])
    return BatchResponse(results=_predict_frame(df))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
