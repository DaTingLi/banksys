# PROGRESS · 项目存档点 〔本项目活记忆 · AI 维护〕

> **作用**:AI 的“游戏存档”。换会话 / 换电脑后,AI 读这里就能接着干。
> **更新时机**:每完成一个里程碑、每次自检通过、每个重要决定后更新。

---

## 1. 当前状态(一句话)

`banksys` 三模块全部完成,**本地四道门禁已跑通**(ruff + pytest 96.98% + AUC=0.8187),
CI/CD 工作流已就绪;Docker 按团队决定改为 **CI/服务器执行,本地不要求**。

## 2. 已完成

- [x] 环境:Miniconda + conda 环境 `envbank`(Python 3.11.15)
- [x] 工程骨架 + 复制 `standards/`(由 standards-template 复制,不改模板)
- [x] 模块1 数据探索:`insights.py`(纯函数,有单测)+ `app.py`(Streamlit)
- [x] 模块2 模型训练:`pipeline.py`(LR/RF/GBDT)+ `model.py`(AUC 门禁 CLI)
- [x] 模块3 在线服务:FastAPI `service.py` + `schemas.py`(/health /predict /predict/batch)
- [x] 测试:26 用例,覆盖率 96.98%
- [x] CI/CD:`ci.yml`(格式+lint+测试+AUC+docker build)、`cd.yml`(SSH 自动部署+健康检查+生产人工卡点)
- [x] 依赖锁版本、Dockerfile、.gitignore、config.yaml
- [x] 活记忆:00 / 01 / PROGRESS

## 3. TODO(下一步)

- [ ] 把改进反哺 `standards-template`(环境/ToS/GBK/Docker-CI-only/分支-PR/Secrets)
- [ ] 产出学生一键复现指南
- [ ] 学员实操:开 feature 分支 → 提 PR(用本人账号)→ CI 绿 → 合并 → 配 Secrets → CD

## 4. 关键决定(ADR 精简版)

- **ADR-1 剔除 `duration`**:通话时长是事后才知道的,属数据泄漏,入模只保留 19 个特征。
- **ADR-2 AUC 而非准确率**:正样本仅约 13%,类别不平衡,准确率会骗人。门槛 AUC≥0.80。
- **ADR-3 预处理+模型同进一个 Pipeline**:保证训练与在线预测变换完全一致,杜绝线上线下不一致。
- **ADR-4 环境用 conda(非 uv)**:学员更熟 conda;`envbank` 统一 Python 3.11。
- **ADR-5 Docker 本地不要求**:很多学员机器没 Docker,本地只跑 ruff/pytest/AUC;`docker build` 交给 CI 与服务器。
- **ADR-6 日志标记用纯 ASCII**:Windows GBK 控制台无法编码 ▶✓✗,改 `>> [OK] [X]`。

## 5. 已知坑(Gotchas,务必让学生避开)

1. **conda 报 CondaToSNonInteractiveError**:新版 conda 默认渠道要先接受服务条款。
   解决:`conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main`(对 main/r/msys2 各执行一次)。
2. **Windows 控制台 UnicodeEncodeError('gbk' 不能编码 \u25b6)**:rich 打印特殊符号在 GBK 终端崩溃。
   解决:日志只用 ASCII 标记(已改);或运行前 `set PYTHONIOENCODING=utf-8` / `chcp 65001`。
   注意:pytest 会捕获输出,所以测试发现不了这个坑,**一定要真正手跑一次 `python -m src.model`**。
3. **pip 慢**:用清华源 `-i https://pypi.tuna.tsinghua.edu.cn/simple`。
4. **Docker COPY models 失败**:`models/` 需存在 → 保留 `.gitkeep`;真模型 `model.pkl` 不进 Git,由训练生成。
5. **直接 push main 不触发评审**:必须开 feature 分支 + PR,CI 才在 PR 上跑。

## 6. 里程碑

- M1 工程化骨架 + CI/CD ✅
- M2 三模块功能完成 ✅
- M3 本地门禁全绿(ruff/pytest/AUC)✅
- M4 GitHub 仓库 + PR + CI 绿 + Secrets + CD 部署 ⏳(学员实操)
