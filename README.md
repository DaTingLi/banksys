# banksys · 银行客户认购预测系统(AI 全栈实战 + CI/CD 参考实现)

> 用历史客户数据预测“客户是否会认购定期存款”,把有限的电话优先打给高潜力客户。
> 三模块:**数据探索(Streamlit)→ 模型训练(AUC 门禁)→ 在线预测(FastAPI)**,全程 CI/CD。
>
> 这是一份**可照做、可复现**的参考实现。本地零 Docker 负担(`docker build` 交给 CI/服务器)。

---

## 0. 你需要准备什么

- 已装 **Miniconda/Anaconda**(用 conda 建环境)
- 已装 **Git**;要做 PR/CI 再装 **GitHub CLI(gh)**
- 数据集 `train.csv`、`test.csv` 已随仓库入库在 `data/`(教学例外:为让 CI 可复现)
- **不需要本地装 Docker**

---

## 1. 一键复现(本地四道门禁)

> Windows PowerShell。`conda` 不在 PATH 时,用 `& "$env:USERPROFILE\miniconda3\Scripts\conda.exe"` 代替 `conda`。

```powershell
# 1) 建环境(若报 ToS 错误,见下方“常见坑”)
conda create -y -n envbank python=3.11
conda activate envbank

# 2) 装依赖(清华源更快)
pip install -r requirements.txt -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3) 四道门禁(全绿才算通过)
ruff format --check .                         # 门禁1 格式
ruff check .                                  # 门禁2 静态检查
pytest --cov=src --cov-fail-under=80 -q       # 门禁3 测试+覆盖率(≥80%)
python -m src.model --check-auc 0.80          # 门禁4 训练+模型 AUC≥0.80,产出 models/model.pkl
```

参考结果:ruff 全绿;**26 用例通过、覆盖率 ~97%**;最佳模型 **GradientBoosting,AUC≈0.819**。

---

## 2. 跑三个模块

```powershell
# 模块1 · 交互式数据探索仪表盘
streamlit run src/data_explorer/app.py

# 模块2 · 训练并保存最佳模型(模块3 依赖它产出的 models/model.pkl)
python -m src.model --check-auc 0.80

# 模块3 · 在线预测服务,然后浏览器打开 http://localhost:8000/docs 调试
uvicorn src.prediction_service.service:app --host 0.0.0.0 --port 8000
```

预测接口示例:

```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{
  "job":"admin.","marital":"married","education":"university.degree","default":"no",
  "housing":"yes","loan":"no","contact":"cellular","month":"may","day_of_week":"mon",
  "poutcome":"nonexistent","age":41,"campaign":2,"pdays":999,"previous":0,
  "emp_var_rate":-1.8,"cons_price_index":92.89,"cons_conf_index":-46.2,
  "lending_rate3m":1.31,"nr_employed":5099.1}'
```

---

## 3. 上 GitHub:分支 → PR → CI → 合并 → CD

> **不要直接 push main**;PR 用你**本人**账号发起。

```powershell
git switch -c feature/1-banksys-init
git add .
git commit -m "feat: banksys 三模块 + CI/CD"
git push -u origin feature/1-banksys-init
gh pr create --base main --title "feat: banksys 初始化" --body "三模块 + CI/CD"
gh run watch          # 等 CI 全绿(GitHub runner 会跑 docker build)
gh pr merge --merge --delete-branch   # 合并后触发 CD
```

### ⚠️ 建仓后第一件事:配置 GitHub Secrets(否则 CD 必失败)

`GitHub → Settings → Secrets and variables → Actions → New repository secret`,配三个:

| Secret | 含义 |
|---|---|
| `SSH_PRIVATE_KEY` | 部署私钥全文(含 `BEGIN/END` 与换行) |
| `SSH_HOST` | 服务器公网 IP / 域名 |
| `SSH_USER` | 部署用户(如 `deploy`) |

服务器前置:已装 Docker、部署目录 `/opt/banksys` 可写、**放行 8000-8010 端口段**。
CD 会自动:同步代码(含 data)→ 容器内训练出 `model.pkl` → `docker build` → 起容器 → `curl /health`。
端口:容器内固定 8000;**主机端口优先 8000,被占用时自动在 8000-8010 选空闲端口**,最终端口会在 CD 日志打印。

---

## 4. 常见坑(Gotchas)

| 现象 | 解决 |
|---|---|
| `CondaToSNonInteractiveError` | 对 main/r/msys2 各跑一次 `conda tos accept --override-channels --channel <渠道URL>` |
| Windows 控制台 `UnicodeEncodeError('gbk' ... \u25b6)` | 打印别用特殊符号(本项目日志已用纯 ASCII);或 `set PYTHONIOENCODING=utf-8` / `chcp 65001`。pytest 会捕获输出掩盖此坑,**务必真跑一次 `python -m src.model`** |
| pip 慢/超时 | 加 `-i https://pypi.tuna.tsinghua.edu.cn/simple` |
| Docker COPY models 失败 | `models/` 要存在(保留 `.gitkeep`);`model.pkl` 由训练生成,不进 Git |
| CD `port is already allocated`(exit 125) | 主机端口被占用;CD 已支持 8000-8010 自动回退,确保防火墙放行该端口段 |
| CD 失败 | 多半是 Secrets 没配 / 服务器没装 Docker / 端口段没放行 |

---

## 5. 目录结构

```text
banksys/
├── standards/                # 项目记忆 + 通用规范(00/01/02.../PROGRESS)
├── data/                     # train.csv / test.csv(不进 Git)
├── src/
│   ├── config.py             # 路径 / 19 个特征 / 门槛
│   ├── common.py             # 中文日志(纯 ASCII 标记)+ 数据加载
│   ├── model.py              # 模块2 入口:训练 + AUC 门禁 CLI
│   ├── data_explorer/        # 模块1:insights(纯函数) + app(Streamlit)
│   ├── model_training/       # 模块2:预处理 + 多模型训练
│   └── prediction_service/   # 模块3:FastAPI service + schemas
├── tests/                    # 单测(CI 跑)
├── models/                   # model.pkl(训练生成,不进 Git)
├── requirements*.txt         # 运行 / 开发依赖(锁版本)
├── pyproject.toml            # ruff / pytest / coverage 配置
├── Dockerfile                # 生产镜像(只装运行依赖)
└── .github/workflows/        # ci.yml(测试)/ cd.yml(部署)
```
