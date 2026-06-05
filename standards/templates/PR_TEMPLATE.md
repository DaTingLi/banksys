# Pull Request 模板

## What

<这个 PR 做了什么>

## Why

关联 Issue:`closes #<编号>`

## How to Test

- [ ] 本地格式检查通过
- [ ] 本地静态检查通过
- [ ] 本地测试通过
- [ ] CI 通过
- [ ] CD / 部署验证通过(如适用)

## 风险与回滚

<风险点;如果失败如何回滚>

## 自检清单

- [ ] 没有硬编码密钥/密码
- [ ] 没有调试 print / 死代码
- [ ] PR 体积可控
- [ ] commit message 符合规范
- [ ] 已同步最新 main,无冲突
- [ ] 已更新 standards/PROGRESS.md

---

通过标准:CI 全绿 + Review 通过 + 分支保护通过。
