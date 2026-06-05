"""pytest 共享夹具：提供一个小样本数据集，避免测试依赖全量数据训练。"""

from __future__ import annotations

import pandas as pd
import pytest

from src.config import RANDOM_STATE, TRAIN_CSV


@pytest.fixture(scope="session")
def sample_df() -> pd.DataFrame:
    """从训练集中抽样 3000 行，保证含正负两类，供单测快速使用。"""
    df = pd.read_csv(TRAIN_CSV)
    return df.sample(n=3000, random_state=RANDOM_STATE).reset_index(drop=True)
