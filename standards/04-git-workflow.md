# 04 · Git 工作流与 PR/Review 标准

> **目标**:定义代码如何从本地安全进入 `main`,并触发 CI/CD。课堂第一项功能必须完整演示本文件第 2 节。

---

## 1. 分支模型:GitHub Flow

```text
main 受保护,永远可部署
 ├─ feature/<issue>-<desc>   新功能
 ├─ fix/<issue>-<desc>       普通缺陷
 ├─ docs/<issue>-<desc>      文档
 └─ chore/<issue>-<desc>     杂务/依赖/配置
```

- 只有一条长期分支:`main`。
- 日常开发必须从 `main` 开短分支,不能直接 push `main`。
- feature 分支寿命建议 ≤ 2-3 天。
- 分支命名:`<类型>/<issue号>-<英文短描述>`,例如 `feature/1-hello-api`。

---

## 2. 课堂必演示:从分支到 CD 的完整命令

> 这段是学生必须亲手跑通的一条链。不要省略 PR,不要直接 push main。

```bash
# 1. 确认在 main,并更新主干
git switch main
git pull

# 2. 从 main 开功能分支
git switch -c feature/1-first-feature

# 3. 写代码 + 写测试后,本地自检
ruff format --check .
ruff check .
pytest

# 4. 提交
git status
git add .
git commit -m "feat: add first feature"

# 5. 推送 feature 分支
git push -u origin feature/1-first-feature

# 6. 创建 PR(AI 做到这里为止)
gh pr create --base main --head feature/1-first-feature --title "feat: add first feature" --body "closes #1"

# 7. 查看 CI(AI 汇报 CI 状态后停下,等人类审核)
gh run list --limit 5
gh run watch

# 8. ★ 合并由人类执行 ★ —— 人工 Review 通过后,由人在网页点 "Merge",或人工运行:
#    gh pr merge <PR号> --merge      # 默认保留分支,不加 --delete-branch
#    AI 不得自行合并未获批准的 PR。

# 9. 合并 main 后会触发 CD,查看部署流水线
gh run list --limit 5
```

> 如果课堂暂时没有开启分支保护,也要按这个流程演示 PR。分支保护是“强制执行”,PR 流程是“正确习惯”。

> **合并是人类的动作,不是 AI 的动作。** AI 在第 6/7 步发起 PR、汇报 CI 后必须停下;
> **只有人工 Review 通过,由人合并**,才触发 CD。AI 绝不替人按下 Merge。

> **默认保留分支**(不加 `--delete-branch`),除非人类明确要求删除已合并分支。

> **PR 必须用你本人 GitHub 账号发起**(`gh auth login` 登录的就是你本人),不要借他人账号代提。

> **⚠️ 建仓后第一件事:配置 Secrets,否则 CD 必失败。**
> 新仓库创建后(CD 第一次跑之前)立刻去
> `GitHub → Settings → Secrets and variables → Actions → New repository secret`
> 配好 `SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(详见 `05-cicd-standards.md` 第 5 节)。
> 没有数据库等部署目标时可只配 SSH 三件套。配置时机:**在合并到 main 触发 CD 之前**。

---

## 3. 认证不要混

| 动作 | 认证方式 | 说明 |
|---|---|---|
| `git push` / `git clone` | SSH 公钥或 HTTPS 凭证 | 负责搬代码 |
| `gh pr create` / `gh run list` | GitHub CLI 登录 | 负责调 GitHub API |
| CD SSH 到服务器 | GitHub Secrets 里的部署私钥 | 由 Actions runner 自动使用 |

如果 SSH 22 端口卡住,可使用 GitHub SSH 443:

```bash
ssh -T -p 443 git@ssh.github.com
git remote set-url origin ssh://git@ssh.github.com:443/<账号>/<仓库>.git
git push
```

---

## 4. 提交信息规范

采用 Conventional Commits:

| 前缀 | 含义 |
|---|---|
| `feat:` | 新功能 |
| `fix:` | 修 bug |
| `docs:` | 文档 |
| `test:` | 测试 |
| `refactor:` | 重构 |
| `ci:` | CI/CD |
| `build:` | 构建/依赖 |
| `chore:` | 杂务 |

一个 commit 只做一件事。

---

## 5. PR 通过三道闸

| 闸 | 内容 | 不通过怎么办 |
|---|---|---|
| 机器闸 | CI 全绿 | 修代码/测试/配置 |
| 人工闸 | 至少 1 人 Review | 修改并回复评论 |
| 策略闸 | 无冲突、分支保护通过 | 同步 main / 解冲突 |

PR 描述必须写:

```text
## What
这个 PR 做了什么

## Why
为什么需要

## Test
- [ ] 本地检查通过
- [ ] CI 通过

closes #<issue号>
```

---

## 6. 冲突处理

```bash
git switch main
git pull
git switch <你的分支>
git rebase main

# 如果有冲突:手动修改文件,删掉 <<<<<<< ======= >>>>>>> 标记
git add <冲突文件>
git rebase --continue

# rebase 后推送
git push --force-with-lease
```

冲突处理后必须重新跑测试。
