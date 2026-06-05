# 05 · CI/CD 标准

> **目标**:定义最小可复现 CI/CD。CI 管“代码是否可靠”,CD 管“可靠代码如何自动上线”。

---

## 1. CI 与 CD

| 名称 | 做什么 | 典型触发 |
|---|---|---|
| CI 持续集成 | 格式、lint、测试、覆盖率、构建 | PR / push |
| CD 持续交付 | 构建可部署产物,部署前可人工审批 | main / tag |
| CD 持续部署 | 合并 main 后自动部署上线 | main |

课堂简版采用:

```text
PR → CI 全绿 → 合并 main → CD 自动部署到服务器 → 健康检查
```

---

## 2. 最小 CI 门禁

| 关卡 | 推荐命令 | 是否必需 |
|---|---|---|
| 格式检查 | `ruff format --check .` 或等价工具 | 必需 |
| 静态检查 | `ruff check .` 或等价工具 | 必需 |
| 单元测试 | `pytest` 或等价工具 | 必需 |
| 覆盖率 | `pytest --cov --cov-fail-under=80` | 推荐 |
| 构建 | `docker build ...` 或项目构建命令 | 必需 |
| 项目特有门禁 | AUC/F1/接口契约/前端构建等 | 按项目 |

CI 红灯时禁止合并。不要靠重跑掩盖问题。

---

## 3. 最小 CD 标准

CD 必须满足:

- 由 GitHub Actions runner 自动触发,不是人手动 SSH。
- 只引用 GitHub Secrets,不硬编码密钥。
- 部署脚本可重复执行。
- 部署后必须健康检查。
- 失败时 Actions 红灯,不能假成功。

推荐触发:

```yaml
on:
  push:
    branches: [ main ]
```

---

## 4. 依赖与镜像构建标准

真实教学环境常见失败:服务器 `docker build` 时从 PyPI / npm / Docker Hub 下载依赖很慢或超时。

通用标准:

| 标准 | 做法 |
|---|---|
| 运行依赖与开发依赖拆分 | 生产镜像只安装运行依赖;测试/lint 工具只在 CI 安装 |
| 镜像源可配置 | Dockerfile 支持镜像源参数,国内服务器可使用国内源 |
| 构建失败即停 | 远程部署脚本第一行 `set -e` |
| 健康检查 | 最后执行 `curl -fsS http://localhost:<PORT>/<HEALTHCHECK>` |
| 可选预热 | 课前在服务器预拉基础镜像,减少等待 |

Python 项目推荐:

```text
requirements.txt      # 生产运行依赖
requirements-dev.txt  # CI/本地检查依赖
```

Dockerfile 推荐:

```dockerfile
ARG PIP_INDEX_URL=https://pypi.org/simple
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt
```

远程部署脚本推荐:

```bash
set -e
docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t <APP>:latest .
docker stop <APP> 2>/dev/null || true
docker rm <APP> 2>/dev/null || true
docker run -d --name <APP> -p <PORT>:<PORT> <APP>:latest
sleep 3
curl -fsS http://localhost:<PORT>/<HEALTHCHECK>
```

---

## 5. Secrets 标准

常用 SSH 部署需要三个 GitHub Actions Secrets:

| Secret | 含义 |
|---|---|
| `SSH_PRIVATE_KEY` | Actions runner 用来登录服务器的私钥全文 |
| `SSH_HOST` | 服务器公网 IP 或域名 |
| `SSH_USER` | 服务器登录用户,如 `root` 或 `deploy` |

规则:

- Secret 名大小写必须一致。
- 私钥必须保留 `BEGIN/END` 和换行。
- Secrets 必须在 CD run 开始前配置好;配置后旧 run 可能需要 rerun。

---

## 6. 排错顺序

| 现象 | 优先检查 |
|---|---|
| `git push` 卡住 | SSH 22 端口是否被拦;可切 GitHub SSH 443 |
| Actions 读不到变量 | Secret 名是否拼错、是否在正确仓库 |
| SSH 登录失败 | 私钥/公钥是否匹配、`authorized_keys`、用户权限 |
| rsync 成功但 docker build 失败 | 依赖下载、镜像源、Dockerfile |
| 服务器本机 curl 通,外网打不开 | 安全组/防火墙是否放行端口 |
| CD 日志二次报错 | 部署脚本是否缺 `set -e` |

---

## 7. 标准总结

1. CI 红灯不合并。
2. CD 必须由 runner 自动触发,不是人手动 SSH。
3. 密钥进 Secrets,脚本进 Git,环境手动配一次。
4. 生产镜像只放运行依赖,开发工具留在 CI。
5. 每次真实故障必须写回 `PROGRESS.md` 和本标准。
