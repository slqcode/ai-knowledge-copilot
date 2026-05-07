# ai-knowledge-copilot

AI Knowledge Copilot 是一个面向知识库问答/RAG 的学习型项目。当前阶段提供 FastAPI 后端骨架、最小前端联调页、测试、Docker 本地启动和 CI 模板。

## 项目结构

```text
ai-knowledge-copilot/
├─ app/                 # 后端应用入口与业务模块
├─ web/                 # 前端界面与联调代码
├─ tests/               # pytest 与集成测试
├─ data/                # 本地样例数据、上传文件、评测集
├─ scripts/             # 启动、导入、评测、清洗脚本
├─ docs/                # 架构图、周报、演示说明
├─ .github/
│  ├─ workflows/        # CI/CD 工作流
│  ├─ PULL_REQUEST_TEMPLATE/
│  └─ ISSUE_TEMPLATE/
├─ docker/              # Docker 镜像配置
│  └─ Dockerfile
├─ README.md            # 项目入口与成果展示
├─ docker-compose.yml   # 本地一键启动
└─ requirements.txt
```

## 当前功能

- `GET /health`：服务健康检查。
- `GET /hello?name=FE`：最小同步接口示例。
- `GET /stream`：SSE 流式接口示例，模拟 AI token/chunk 输出。
- `web/index.html`：浏览器内的最小联调页面。
- `scripts/import_data.py`：本地数据导入占位脚本，后续可扩展为文档解析、切片、embedding 与入库流程。

## 快速开始

```bash
cd ai-knowledge-copilot
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

如果没有 `python3.11`，可使用任意 Python 3.11+ 解释器。

## 本地访问

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Hello: http://127.0.0.1:8000/hello?name=FE
- Stream: http://127.0.0.1:8000/stream
- 前端联调页：直接用浏览器打开 `web/index.html`

## 常用命令

```bash
# 启动后端；如果没有 .env，会自动从 .env.example 复制
./scripts/dev.sh

# 运行测试
pytest -q
# 或
./scripts/test.sh

# 运行导入占位脚本
python -m scripts.import_data data
```

## Docker 一键启动

```bash
cp .env.example .env
docker compose up --build
```

## 配置

复制 `.env.example` 到 `.env` 后按需调整：

```bash
cp .env.example .env
```

不要提交真实 API Key。运行时配置从 `.env` 读取。

## 文档

- `docs/week1.md`：第 1 周实作指南。
- `docs/WEEK1_EXECUTION_NOTES.md`：第 1 周执行过程说明。

## 常见问题

- 端口占用：修改 `docker-compose.yml` 的端口映射，例如 `8001:8000`。
- CORS 报错：把前端来源加入 `CORS_ORIGINS`。
- 流式接口等待较久：默认每秒输出一个事件；测试中会把延迟临时设为 0。
