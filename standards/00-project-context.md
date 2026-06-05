# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的“身份档案”。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`banksys`(银行客户认购预测系统)
- **一句话目标**:用历史客户数据预测客户是否会认购定期存款,把有限的电话优先打给高潜力客户。
- **使用者/受益者**:银行电话营销团队(降本增效、减少骚扰);课堂学员(学 AI 全栈 + CI/CD)。
- **核心功能**:
  - 模块1:Streamlit 交互式数据探索仪表盘(动态筛选 + Plotly 可视化 + 特征洞察)
  - 模块2:多模型训练与评估(LR / RF / GBDT),按 AUC 选最佳并保存 `models/model.pkl`
  - 模块3:FastAPI 在线预测服务(`/predict` 单条 + 批量,`/health` 健康检查)
- **输入/数据**:阿里云天池《银行客户认购预测》。`train.csv` 22500 行(带标签)、`test.csv` 7500 行(无标签)。**数据不进 Git**(放 `data/`,已在 .gitignore)。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11(conda 环境 `envbank`) | 课程统一;ML 生态在 3.11 上轮子最稳(3.14 太新,部分库无轮子) |
| 数据/ML | pandas + scikit-learn | 通用、可复现;XGBoost/LightGBM 作为可选增强,不进默认依赖 |
| 数据探索 UI | Streamlit + Plotly | 交互式仪表盘,几行代码出图 |
| 在线服务 | FastAPI + uvicorn/gunicorn | 自带 /docs;gunicorn+uvicorn worker 生产更稳 |
| 测试 | pytest + pytest-cov + httpx | 单测 + 覆盖率 + FastAPI TestClient |
| 格式/静态检查 | ruff(format + check) | 一个工具搞定格式与 lint |
| 打包/运行 | Docker(python:3.11-slim) | 生产镜像只装运行依赖 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学 |

## 3. 目录地图

```text
banksys/
├── standards/                  # AI 项目记忆与通用规范(本目录)
├── data/                       # train.csv / test.csv(不进 Git)
├── src/
│   ├── config.py               # 路径 / 字段定义 / 门槛
│   ├── common.py               # rich 中文日志 + 数据加载
│   ├── model.py                # 模块2 入口:训练+保存+AUC 门禁 CLI
│   ├── data_explorer/          # 模块1:insights(纯函数) + app(Streamlit)
│   ├── model_training/         # 模块2:预处理 + 多模型训练 pipeline
│   └── prediction_service/     # 模块3:FastAPI service + schemas
├── models/                     # 产出 model.pkl(不进 Git,留 .gitkeep)
├── tests/                      # 单测(CI 跑这些)
├── requirements.txt            # 生产运行依赖
├── requirements-dev.txt        # 本地/CI 检查依赖(含 streamlit/plotly)
├── pyproject.toml              # ruff / pytest / coverage 配置
├── Dockerfile                  # 生产镜像(只装运行依赖)
├── config.yaml                 # 非敏感配置(无密钥)
└── .github/workflows/
    ├── ci.yml                  # 自动测试
    └── cd.yml                  # 自动部署
```

## 4. 质量门槛

> **本地必跑(零 Docker)** 与 **CI/CD 跑**分工:学员本地不装 Docker,只跑前 4 项;
> `docker build` 只在 GitHub Actions(CI)与服务器(CD)执行,避免本地环境复杂度。

| 类型 | 命令 | 本地必跑 | CI 跑 |
|---|---|:---:|:---:|
| 格式检查 | `ruff format --check .` | ✅ | ✅ |
| 静态检查 | `ruff check .` | ✅ | ✅ |
| 单元测试+覆盖率 | `pytest --cov=src --cov-fail-under=80`(≥80%,`app.py` omit) | ✅ | ✅ |
| 模型指标 | `python -m src.model --check-auc 0.80`(验证集 **AUC≥0.80**) | ✅ | ✅ |
| 镜像构建 | `docker build`(只在云端/服务器) | ❌ 不要求 | ✅ |

最近一次本地自检结果:ruff 全绿;26 用例通过、覆盖率 96.98%;最佳模型 GradientBoosting **AUC=0.8187**。

## 5. 不变约束

- 密钥、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- `model.pkl` **不进 Git**(由训练生成)。
- 教学数据集 `train.csv`/`test.csv` **已入库**(为保证 CI 的 pytest 与 AUC 门禁在干净 runner 上可复现);生产/敏感数据切勿照搬此例外。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR(PR 才触发 CI/CD)。
- CI 红灯不合并。
- `duration` 字段有数据泄漏,**入模特征已剔除**(只保留 19 个特征)。

## 6. 部署/CI 占位符取值

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys` | 镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys` | 服务器部署目录 |
| `<PORT>` | `8000` | 服务端口 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/health` | 健康检查地址 |
| `<SSH_USER>` | `deploy` | 部署用户 |
| `<SSH_HOST>` | `<服务器公网 IP>` | 配在 GitHub Secrets,不写进文件 |
| `<质量门槛>` | `AUC≥0.80` | 模型门禁 |
