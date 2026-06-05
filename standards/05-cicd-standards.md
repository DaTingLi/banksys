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

| 关卡 | 推荐命令 | 本地必跑 | CI 必跑 |
|---|---|:---:|:---:|
| 格式检查 | `ruff format --check .` 或等价工具 | ✅ | ✅ |
| 静态检查 | `ruff check .` 或等价工具 | ✅ | ✅ |
| 单元测试 | `pytest` 或等价工具 | ✅ | ✅ |
| 覆盖率 | `pytest --cov --cov-fail-under=80` | ✅ | ✅ |
| 项目特有门禁 | AUC/F1/接口契约/前端构建等 | ✅ | ✅ |
| 构建 | `docker build ...` 或项目构建命令 | ❌ 不要求 | ✅ |

CI 红灯时禁止合并。不要靠重跑掩盖问题。

> **本地不强制装 Docker**:很多学员/开发机没有 Docker,本地装它只会增加复杂度。
> 约定 **本地只跑前几项门禁,`docker build` 交给 CI(云端 runner 自带 Docker)与服务器(CD)**。
> 这样本地零 Docker 负担,镜像构建仍有 CI 兜底。是否要本地构建,**按机器情况决定或先问开发者**。

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

远程部署脚本推荐(含幂等替换 + 端口自动回退):

```bash
set -e
docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t <APP>:latest .

# 端口:容器内端口固定;主机端口优先 <PORT>,被占用就在预留区间自动找空闲端口。
port_in_use() {
  ss -ltnH 2>/dev/null | grep -q ":$1 " && return 0
  docker ps --format "{{.Ports}}" 2>/dev/null | grep -q ":$1->" && return 0
  return 1
}
PORT=""
for p in $(seq <PORT> <PORT_MAX>); do
  if ! port_in_use "$p"; then PORT="$p"; break; fi
done
[ -z "$PORT" ] && { echo "预留端口区间已全部占用,部署中止"; exit 1; }
echo ">> 部署到主机端口 $PORT"

docker rm -f <APP> 2>/dev/null || true   # 一步停删自身旧容器,幂等可重跑
docker run -d --name <APP> --restart unless-stopped -p ${PORT}:<容器内端口> <APP>:latest
sleep 3
curl -fsS "http://localhost:${PORT}/<HEALTHCHECK>"
echo ">> 部署成功:http://<SSH_HOST>:${PORT}/<HEALTHCHECK>"
```

> **端口标准**:容器内端口固定,**主机端口可回退**(预留如 `<PORT>`-`<PORT_MAX>` 一段)。
> 起容器用 `docker rm -f <APP>` 一步停删自身旧容器保证幂等;**不要**盲目删除占用端口的他人容器。
> 防火墙/安全组要放行整段预留端口;最终落在哪个端口由 CD 日志打印。
> 踩坑:`docker run` 报 `port is already allocated`(exit 125)就是主机端口被占用所致。

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

## 6. 本地环境准备(一次性)

环境怎么建,**写进标准、可复现**。优先级:`uv` → `uv` 不行用 `conda` → 再不行用系统 `venv`。
本课程学员更熟 `conda`,默认用 conda:

```bash
# 1) 建并激活环境(示例环境名 envproj,Python 版本按项目 00 文档)
conda create -y -n envproj python=3.11
conda activate envproj

# 2) 装依赖(国内用清华源更快)
pip install -r requirements.txt -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> **坑:`CondaToSNonInteractiveError`(新版 conda 默认渠道未接受服务条款)**。
> 解决,对三个渠道各执行一次:
> ```bash
> conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
> conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
> conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
> ```

---

## 7. 排错顺序

| 现象 | 优先检查 |
|---|---|
| `conda create` 报 ToS 错误 | 执行上面的 `conda tos accept`(main/r/msys2) |
| Windows 控制台 `UnicodeEncodeError('gbk' ... \u25b6)` | 日志/打印含特殊符号;改用纯 ASCII,或 `set PYTHONIOENCODING=utf-8` / `chcp 65001`。注意 pytest 会捕获输出掩盖此坑,必须真跑一次脚本 |
| CI 红:`FileNotFoundError` 找不到数据 | 数据被 `.gitignore` 排除,干净 runner 上没有。公开教学数据可入库;敏感数据则在 CI 里下载/造样本 |
| `docker run` 报 `port is already allocated`(exit 125) | 主机端口被占用;容器内端口固定、主机端口在预留区间自动回退(见第 4 节);`docker rm -f <APP>` 幂等替换自身 |
| `git push` 卡住/`Recv failure`/`Connection reset` | SSH 22 被拦可切 443;HTTPS 偶发抖动则重试几次 |
| Actions 读不到变量 | Secret 名是否拼错、是否在正确仓库 |
| SSH 登录失败 | 私钥/公钥是否匹配、`authorized_keys`、用户权限 |
| rsync 成功但 docker build 失败 | 依赖下载、镜像源、Dockerfile |
| 服务器本机 curl 通,外网打不开 | 安全组/防火墙是否放行端口(含回退端口段) |
| CD 日志二次报错 | 部署脚本是否缺 `set -e` |

---

## 8. 标准总结

1. CI 红灯不合并。
2. CD 必须由 runner 自动触发,不是人手动 SSH。
3. 密钥进 Secrets,脚本进 Git,环境手动配一次。
4. 生产镜像只放运行依赖,开发工具留在 CI;**本地不强制装 Docker**。
5. 每次真实故障必须写回 `PROGRESS.md` 和本标准。
