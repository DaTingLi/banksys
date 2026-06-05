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

## 5. 标准开发闭环

```text
读 standards
  → 从 main 开 feature 分支
  → 写代码 + 测试
  → 本地自检
  → commit
  → push feature 分支
  → 创建 PR
  → CI 自动检查
  → Review + 分支保护通过
  → 合并 main
  → CD 自动部署
  → 验证 /health 或业务验收
  → 写回 PROGRESS
```

**课堂第一项功能必须完整演示一次这条链**,不能直接 push main。

---

## 6. 反臃肿纪律

1. 需求只写进 `01-requirements.md`,不要到处新建 PRD。
2. 进度、决策、坑只写进 `PROGRESS.md`。
3. 一需求一分支一 PR,PR 尽量小于 400 行。
4. CI 红灯不合并;flaky test 必须根治。
5. 新增目录前先更新 `00-project-context.md` 的目录地图。
