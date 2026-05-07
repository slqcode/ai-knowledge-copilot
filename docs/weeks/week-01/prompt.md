---
title: Week 01 Prompt
week: 01
type: prompt
tool: Claude Code
status: completed
---

# Week 01 Prompt：FastAPI 基础服务

## Prompt 背景与目标

本周只追一个结果：把本地可运行的 **FastAPI 基础服务**搭起来，并完成两个同步接口与一个最小流式 SSE 接口；同时把虚拟环境、测试、日志、Docker 和 README 基础骨架一次性补齐。这样第 2 周你就能直接进入文件上传、Pydantic、异步与前后端联调，而不是反复返工环境。citeturn0search16turn0search1turn0search2

## 本周目标与验收标准

量化目标：一是本地能启动 `http://127.0.0.1:8000`；二是 `/health`、`/hello`、`/stream` 三个接口可用；三是 `pytest -q` 通过；四是 `docker compose up --build` 可一键启动；五是 README 能让别人 10–15 分钟跑通。FastAPI 官方文档把“虚拟环境 + 安装 + 路由 + 自动文档”作为最小起点；Python 官方也明确建议使用 `venv` 和 `pip` 做隔离环境。citeturn0search16turn0search8turn0search9turn0search17

## 环境准备

建议 Python **3.11**；理由是生态成熟、与你本阶段依赖兼容性更稳。包管理用内置 `pip`，虚拟环境用 `venv`。FastAPI 官方推荐在虚拟环境里安装依赖；Python Packaging Guide 也给出 `venv + pip + requirements.txt` 的标准流程。citeturn0search16turn0search1turn0search13

| 系统 | 命令 |
|---|---|
| macOS | `brew install python@3.11 && python3.11 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip && python -m pip install -r requirements.txt` |
| Linux Debian/Ubuntu | `sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip && python3.11 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip && python -m pip install -r requirements.txt` |
| Windows PowerShell | `winget install -e --id Python.Python.3.11 ; py -3.11 -m venv .venv ; .\.venv\Scripts\Activate.ps1 ; python -m pip install -U pip ; python -m pip install -r requirements.txt` |

`requirements.txt` 选这些包：`fastapi[standard]` 做 Web/API；`pydantic-settings` 读环境变量；`python-dotenv` 支持 `.env`；`pytest` 做最小测试；`httpx` 给测试客户端与后续调用留钩子。FastAPI 官方安装示例直接使用 `fastapi[standard]`；OpenAI 官方 SDK 也建议用环境变量或 `.env` 管理密钥，不要写死在代码里。citeturn0search16turn0search3turn0search11

```txt
# requirements.txt
fastapi[standard]
pydantic-settings
python-dotenv
pytest
httpx
```

## 项目结构与代码

目录建议如下；Week1 不上数据库，先把接口骨架、未来数据模型和 ingest 占位留好。FastAPI 官方也提供了按模块拆分更大应用的结构化写法。citeturn0search8turn2search1

```text
ai-knowledge-copilot/
├─ app/
│  ├─ main.py
│  ├─ schemas.py
│  ├─ models.py
│  └─ ingest.py
├─ tests/
│  └─ test_main.py
├─ data/
├─ .env.example
├─ requirements.txt
├─ docker/Dockerfile
├─ docker-compose.yml
└─ README.md
```

```python
# app/schemas.py
from pydantic import BaseModel

class HealthResp(BaseModel):
    status: str = "ok"
    app: str
    env: str

class HelloResp(BaseModel):
    message: str
```

```python
# app/models.py
from dataclasses import dataclass

@dataclass
class DocumentChunk:  # 先占位，后面做文档切块会用到
    doc_id: str
    chunk_id: str
    text: str
    source: str | None = None
```

```python
# app/ingest.py
from pathlib import Path

def run(path: str = "data"):
    p = Path(path)
    print(f"[ingest] 占位：未来在 {p.resolve()} 下处理文件")

if __name__ == "__main__":
    run()
```

```python
# app/main.py
import asyncio, json, logging, time, uuid
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic_settings import BaseSettings, SettingsConfigDict
from .schemas import HealthResp, HelloResp

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    APP_NAME: str = "ai-knowledge-copilot"
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

settings = Settings()
logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("app")

app = FastAPI(title=settings.APP_NAME)  # 自动生成 /docs

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.CORS_ORIGINS.split(",") if x.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    rid = str(uuid.uuid4())  # 请求ID，后续排障会用到
    start = time.time()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled path=%s rid=%s", request.url.path, rid)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error", "request_id": rid})
    response.headers["X-Request-Id"] = rid
    logger.info("path=%s status=%s cost_ms=%.2f rid=%s", request.url.path, response.status_code, (time.time()-start)*1000, rid)
    return response

@app.get("/health", response_model=HealthResp)
async def health():
    return HealthResp(app=settings.APP_NAME, env=settings.APP_ENV)

@app.get("/hello", response_model=HelloResp)
async def hello(name: str = Query("world", min_length=1, max_length=50)):
    return HelloResp(message=f"Hello, {name}")

async def event_gen():
    for i in range(1, 6):
        yield f"data: {json.dumps({'token': f'chunk-{i}'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(1)  # 给事件循环可取消点

@app.get("/stream")
async def stream():
    return StreamingResponse(event_gen(), media_type="text/event-stream")
```

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_hello():
    r = client.get("/hello", params={"name": "FE"})
    assert r.status_code == 200
    assert r.json()["message"] == "Hello, FE"
```

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY tests ./tests
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./app:/app/app
      - ./tests:/app/tests
      - ./data:/app/data
```

```env
# .env.example
APP_NAME=ai-knowledge-copilot
APP_ENV=dev
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
OPENAI_API_KEY=
```

```md
# README.md
## 项目简介
Week1 FastAPI 骨架：health / hello / stream。

## 快速开始
1. 复制 `.env.example` 为 `.env`
2. 创建虚拟环境并安装依赖
3. `uvicorn app.main:app --reload`

## 本地访问
- Docs: `/docs`
- Health: `/health`
- Hello: `/hello?name=FE`
- Stream: `/stream`

## 测试
`pytest -q`

## Docker
`docker compose up --build`

## 常见问题
- 端口占用：换 `8001:8000`
- CORS 报错：把前端地址加入 `CORS_ORIGINS`
```

## 运行、联调、测试与排障

启动：`cp .env.example .env && uvicorn app.main:app --reload`。验证：浏览器开 `http://127.0.0.1:8000/docs`；命令行用 `curl http://127.0.0.1:8000/health`、`curl "http://127.0.0.1:8000/hello?name=FE"`、`curl -N http://127.0.0.1:8000/stream`。FastAPI 会自动提供 OpenAPI 文档；`StreamingResponse` 适合最小流式返回；浏览器用 `EventSource` 连接 `text/event-stream` 最直接。citeturn0search8turn2search0turn1search1turn1search3

```ts
// 前端 EventSource
const es = new EventSource("http://127.0.0.1:8000/stream");
es.onmessage = (e) => console.log(JSON.parse(e.data));
```

```ts
// 前端 fetch streaming
const res = await fetch("http://127.0.0.1:8000/stream");
const reader = res.body!.getReader();
const decoder = new TextDecoder();
while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  console.log(decoder.decode(value));
}
```

测试与 CI 通用步骤：装 Python 3.11 → 建虚拟环境 → `python -m pip install -r requirements.txt` → `pytest -q`。如果任意 CI 平台未指定，先用这 4 步就够；后续再加 lint。pytest 官方把“安装、写首个测试、执行测试”作为最小路径。citeturn1search0turn1search2

Docker 一键启动：`docker compose up --build`。常见故障：8000 端口被占用；`.env` 未复制；Windows PowerShell 未信任脚本需执行策略；前端跨域没把源地址放进 `CORS_ORIGINS`。Docker 官方说明 Compose 适合用一个 YAML 定义多容器、端口、卷和日志；FastAPI 官方也提醒 CORS 在带凭证时不能全量通配。citeturn0search10turn0search2turn2search15

## 安全与工程注意事项

本周必须养成三个习惯：第一，**不要把 API Key 写进源码**，统一放 `.env`，并把 `.env` 加入 `.gitignore`；第二，CORS 只放必要源地址；第三，开发端口、日志级别和未来数据目录都走环境变量。云账号、预算、生产模型供应商均为**未指定**，因此 Week1 建议全部本地跑；如后续要接模型，优先选环境变量注入密钥、最小权限、按项目隔离。OpenAI 官方 SDK 与 Agents 文档都推荐通过 `OPENAI_API_KEY` 环境变量提供密钥。citeturn0search3turn0search11turn0search15

## 主要参考来源

Python `venv` / `pip` / requirements：citeturn0search1turn0search9turn0search17  
FastAPI 安装、首个应用、CORS、错误处理、中间件、流式响应：citeturn0search16turn0search8turn0search0turn0search4turn2search0turn2search1  
docker/Dockerfile 与 Compose：citeturn0search2turn0search6turn0search10turn0search18  
pytest：citeturn1search0turn1search2  
浏览器 SSE / EventSource：citeturn1search1turn1search3  
entity["company","OpenAI","ai company"] Python SDK 与环境变量：citeturn0search3turn0search11turn0search15