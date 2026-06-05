"""通用工具：简体中文 rich 日志与数据加载。

所有模块共享同一套日志风格，保证课堂演示与排错时输出统一。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.theme import Theme

# 统一配色：成功=绿、警告=黄、错误=红、提示=青。
_theme = Theme(
    {
        "ok": "bold green",
        "warn": "bold yellow",
        "err": "bold red",
        "info": "bold cyan",
        "step": "bold magenta",
    }
)
console = Console(theme=_theme)


# 标记一律用纯 ASCII:Windows GBK 控制台无法编码 ▶ ✓ ✗ 等字符,会直接崩溃。
def log_step(message: str) -> None:
    """打印一个步骤标题。"""
    console.print(f"[step]>> {message}[/step]")


def log_ok(message: str) -> None:
    """打印成功信息。"""
    console.print(f"[ok][OK] {message}[/ok]")


def log_warn(message: str) -> None:
    """打印警告信息。"""
    console.print(f"[warn][!] {message}[/warn]")


def log_err(message: str) -> None:
    """打印错误信息。"""
    console.print(f"[err][X] {message}[/err]")


def log_info(message: str) -> None:
    """打印普通提示。"""
    console.print(f"[info]- {message}[/info]")


def load_csv(path: str | Path) -> pd.DataFrame:
    """读取 CSV，文件缺失时给出明确的中文报错。"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"找不到数据文件：{path}。请确认 train.csv / test.csv 已放入 data/ 目录。"
        )
    return pd.read_csv(path)
