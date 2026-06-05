# standards-template · 学生项目可复制模板

> **用途**:每个新项目复制一份本目录,改名为项目根目录下的 `standards/`。任意 AI 工具进入项目后,先读 `standards/README.md`,即可按统一规则继续开发、提交、PR、CI/CD 与存档。

---

## 1. 学生怎么用

```bash
# 在你的项目根目录执行
cp -r <课件目录>/standards-template ./standards
```

Windows 可手动复制文件夹,复制后目录应是:

```text
你的项目/
├── standards/
│   ├── README.md
│   ├── 00-project-context.md
│   ├── 01-requirements.md
│   ├── PROGRESS.md
│   ├── 02-coding-standards.md
│   ├── 03-testing-standards.md
│   ├── 04-git-workflow.md
│   ├── 05-cicd-standards.md
│   ├── 06-ai-collab-protocol.md
│   └── templates/
└── <你的代码>
```

---

## 2. 两类文件,不要混

| 类型 | 文件 | 是否每个项目要改 | 谁维护 |
|---|---|---|---|
| **项目活记忆** | `00-project-context.md`、`01-requirements.md`、`PROGRESS.md` | 必须按项目重填 | AI 写,人审 |
| **通用规范** | `02`~`06`、`templates/` | 默认不改 | 团队维护 |

> 简单说:`00/01/PROGRESS` 记录“这个项目是什么、要做什么、做到哪了”;`02~06` 规定“怎么写代码、怎么测试、怎么走 Git/PR/CI/CD”。

---

## 3. AI 每次会话读取顺序

1. `00-project-context.md` — 项目身份、技术栈、目录地图、部署取值。
2. `01-requirements.md` — 活 PRD,所有需求与验收标准。
3. `PROGRESS.md` — 当前状态、下一步、决策、踩坑。
4. `02`~`06` — 通用工程规范。
5. `templates/` — Issue / PR 模板。

---

## 4. 第一次开工 prompt

```prompt
请先读取 standards/README.md,并按它的顺序读取 00/01/PROGRESS 与 02~06。
这是一个新项目。我的项目需求是:
<在这里写项目目标、技术栈、希望实现的功能、部署方式>

请先做三件事:
1. 填写 standards/00-project-context.md。
2. 把需求整理进 standards/01-requirements.md,写成用户故事和验收标准。
3. 初始化 standards/PROGRESS.md,列出第一批 TODO。

完成后先停下让我确认,不要直接写代码。
```

---

## 5. 标准开发闭环 · 固定六步(每步确认)

AI 严格按 `06-ai-collab-protocol.md` 的「六步交付流程 + 确认门」推进,**每到确认门停下汇报、等人确认**:

```text
① 建仓 + 配 Secrets    AI 建仓 → ✋提示人类配 SSH_PRIVATE_KEY/HOST/USER(新仓库默认没有)
② 开 feature 分支       从 main 切分支,严禁直接改 main         ✋报分支名
③ 本地模块化开发        逐模块写代码+测试,每模块更新 PROGRESS  ✋每个模块汇报进度
④ 本地 CI 自检(AI 跑)  ruff + pytest + 覆盖率 + 项目门禁;本地不强制 docker  ✋全绿才继续
⑤ 触发 PR              push + AI 主动建 PR,CI 在 PR 上复检    ✋报 PR 链接 + CI 状态
⑥ 人工审核 →(人)合并 → CD  ✋AI 发完 PR 即停;Review 与 Merge 都由人做;合并触发 CD → ✋报端口/健康检查
```

**课堂第一项功能必须完整演示一次这条链**,不能直接 push main;
**合并是人类的动作——AI 绝不自行合并 PR;分支默认保留(不自动删)。**

---

## 6. 反臃肿纪律

1. 需求只写进 `01-requirements.md`,不要到处新建 PRD。
2. 进度、决策、坑只写进 `PROGRESS.md`。
3. 一需求一分支一 PR,PR 尽量小于 400 行。
4. CI 红灯不合并;flaky test 必须根治。
5. 新增目录前先更新 `00-project-context.md` 的目录地图。
