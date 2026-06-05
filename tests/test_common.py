"""通用工具单元测试：日志与数据加载。"""

from __future__ import annotations

import pandas as pd
import pytest

from src import common


def test_log_helpers_do_not_raise():
    # 日志函数只需保证可调用、不抛错。
    common.log_step("step")
    common.log_ok("ok")
    common.log_warn("warn")
    common.log_err("err")
    common.log_info("info")


def test_load_csv_reads_file(tmp_path):
    p = tmp_path / "x.csv"
    pd.DataFrame({"a": [1, 2]}).to_csv(p, index=False)
    df = common.load_csv(p)
    assert df.shape == (2, 1)


def test_load_csv_missing_raises():
    with pytest.raises(FileNotFoundError):
        common.load_csv("不存在的文件.csv")
