"""模块2 · 数据预处理与多模型训练核心逻辑。

设计要点：
- 预处理与模型封进同一个 sklearn Pipeline，保证训练与在线预测使用完全一致的变换。
- 显式剔除 duration（数据泄漏）与 id（标识列）。
- 类别不平衡（正样本约 13%），用 class_weight / AUC 等指标评估，而非准确率。
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    POSITIVE_LABEL,
    RANDOM_STATE,
    TARGET,
)


@dataclass
class ModelResult:
    """单个模型的评估结果。"""

    name: str
    pipeline: Pipeline
    auc: float
    precision: float
    recall: float
    f1: float


def prepare_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """从原始 DataFrame 切出特征矩阵 X 与标签 y(0/1)。"""
    if TARGET not in df.columns:
        raise ValueError("数据缺少目标列 subscribe，无法训练。")
    x = df[list(FEATURE_COLUMNS)].copy()
    y = (df[TARGET] == POSITIVE_LABEL).astype(int)
    return x, y


def build_preprocessor() -> ColumnTransformer:
    """构建列变换器：类别 OneHot + 数值标准化。"""
    return ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                list(CATEGORICAL_FEATURES),
            ),
            ("num", StandardScaler(), list(NUMERIC_FEATURES)),
        ]
    )


def _candidate_models() -> dict[str, object]:
    """候选模型集合：逻辑回归 / 随机森林 / 梯度提升。

    全部来自 scikit-learn，保证任意环境可复现；
    如需 XGBoost / LightGBM 可作为可选增强，不作为默认依赖。
    """
    return {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def train_and_select(
    df: pd.DataFrame, test_size: float = 0.2
) -> tuple[ModelResult, list[ModelResult]]:
    """训练所有候选模型并按验证集 AUC 选出最佳。

    返回 (最佳模型结果, 全部模型结果列表)。
    """
    x, y = prepare_xy(df)
    x_train, x_valid, y_train, y_valid = train_test_split(
        x, y, test_size=test_size, stratify=y, random_state=RANDOM_STATE
    )

    results: list[ModelResult] = []
    for name, estimator in _candidate_models().items():
        pipe = Pipeline(steps=[("prep", build_preprocessor()), ("clf", estimator)])
        pipe.fit(x_train, y_train)
        proba = pipe.predict_proba(x_valid)[:, 1]
        pred = (proba >= 0.5).astype(int)
        results.append(
            ModelResult(
                name=name,
                pipeline=pipe,
                auc=float(roc_auc_score(y_valid, proba)),
                precision=float(precision_score(y_valid, pred, zero_division=0)),
                recall=float(recall_score(y_valid, pred, zero_division=0)),
                f1=float(f1_score(y_valid, pred, zero_division=0)),
            )
        )

    best = max(results, key=lambda r: r.auc)
    return best, results
