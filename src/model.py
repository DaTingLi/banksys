"""模块2 入口 · 训练、评估、保存模型，并提供 CI 质量门禁。

用法：
    python -m src.model                 # 训练并保存 models/model.pkl
    python -m src.model --check-auc 0.80  # 训练后校验 AUC≥阈值，不达标退出码=1（CI 红灯）

CI 在 ci.yml 里调用：python -m src.model --check-auc 0.80
"""

from __future__ import annotations

import argparse
import sys

import joblib

from src.common import load_csv, log_err, log_info, log_ok, log_step
from src.config import (
    DEFAULT_AUC_GATE,
    MODEL_PATH,
    MODELS_DIR,
    TRAIN_CSV,
)
from src.model_training.pipeline import ModelResult, train_and_select


def train(data_path=None) -> ModelResult:
    """训练全部候选模型，保存最佳模型到 models/model.pkl。

    data_path 为空时使用配置里的 TRAIN_CSV；显式传入可便于测试注入小数据集。
    """
    log_step("加载训练数据")
    df = load_csv(data_path or TRAIN_CSV)
    log_info(f"样本量：{len(df)} 行")

    log_step("训练并选择最佳模型（LR / RF / GBDT）")
    best, results = train_and_select(df)
    for r in results:
        log_info(
            f"{r.name:>18} | AUC={r.auc:.4f} P={r.precision:.3f} " f"R={r.recall:.3f} F1={r.f1:.3f}"
        )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best.pipeline, MODEL_PATH)
    log_ok(f"最佳模型：{best.name}（AUC={best.auc:.4f}）已保存到 {MODEL_PATH}")
    return best


def main(argv: list[str] | None = None) -> int:
    """命令行入口。返回进程退出码。"""
    parser = argparse.ArgumentParser(description="银行认购模型训练与质量门禁")
    parser.add_argument(
        "--check-auc",
        type=float,
        default=None,
        metavar="THRESHOLD",
        help=f"AUC 质量门槛，默认建议 {DEFAULT_AUC_GATE}",
    )
    args = parser.parse_args(argv)

    best = train()

    if args.check_auc is not None:
        if best.auc < args.check_auc:
            log_err(f"AUC 门禁未通过：{best.auc:.4f} < {args.check_auc:.2f}，CI 应红灯。")
            return 1
        log_ok(f"AUC 门禁通过：{best.auc:.4f} ≥ {args.check_auc:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
