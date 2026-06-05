"""项目级配置：路径、字段定义、模型门槛。

集中维护“数据在哪、特征有哪些、门槛是多少”，避免散落到各模块。
"""

from __future__ import annotations

from pathlib import Path

# 目录锚点：以本文件为基准向上定位项目根，避免依赖运行时工作目录。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"

TRAIN_CSV = DATA_DIR / "train.csv"
TEST_CSV = DATA_DIR / "test.csv"
MODEL_PATH = MODELS_DIR / "model.pkl"

# 目标列与正样本取值。
TARGET = "subscribe"
POSITIVE_LABEL = "yes"

# 标识列，不参与建模。
ID_COLUMN = "id"

# 数据泄漏字段：通话时长只有打完电话才知道，事前打分拿不到，必须剔除。
LEAKAGE_FEATURES = ("duration",)

# 类别型特征（OneHot 编码）。
CATEGORICAL_FEATURES = (
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
)

# 数值型特征（标准化）。
NUMERIC_FEATURES = (
    "age",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
)

# 入模特征 = 类别 + 数值（共 19 个，已剔除 id / duration / subscribe）。
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# 模型质量门槛：AUC 不达标则 CI 红灯。
DEFAULT_AUC_GATE = 0.80

# 在线服务端口（与 00-project-context.md 第 6 节占位符一致）。
SERVICE_PORT = 8000

# 复现实验用的固定随机种子。
RANDOM_STATE = 42
