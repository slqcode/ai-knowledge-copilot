---
title: Week 01 Claude Code Summary
week: 01
type: execution-summary
tool: Claude Code
status: completed
---

# Week 01 Claude Code 执行总结

这份文档解释本次任务中我实际做了什么、为什么这么做，以及这些内容和前端开发之间的关系。你可以把它当作一份“零 Python 基础前端工程师入门 FastAPI”的项目笔记。

## 1. 先读取 `docs/weeks/week-01/prompt.md`

我首先打开了 `docs/weeks/week-01/prompt.md`，它是一份第 1 周实作指南。

它要求完成的核心目标是：

1. 搭建一个本地可运行的 FastAPI 服务。
2. 提供 3 个接口：`/health`、`/hello`、`/stream`。
3. 准备 Python 虚拟环境和依赖文件。
4. 添加测试。
5. 添加日志、中间件、Docker 和 README。
6. 最终能本地启动 `http://127.0.0.1:8000`。

对前端开发者来说，这一步类似于你先阅读产品需求文档或技术方案，明确要做哪些页面、接口、依赖和验收标准。

## 2. 检查当前项目目录

当时项目里只有：

```text
docs/weeks/week-01/prompt.md
```

也就是说，这不是一个已经初始化好的 Python 项目，而是一个空目录加一份执行指南。

我还检查了 Git 状态，发现当前目录不是 Git 仓库：

```text
fatal: not a git repository
```

这说明本次操作不涉及 Git commit，也不需要考虑现有分支或未提交改动。

## 3. 创建项目目录结构

根据 `docs/weeks/week-01/prompt.md` 的要求，我创建了这些目录：

```text
app/
tests/
data/
```

它们的作用分别是：

```text
app/    放后端应用代码
tests/  放自动化测试
data/   预留给后续文件上传、知识库文档、切片数据等
```

前端类比：

```text
src/      业务代码
tests/    测试代码
public/   静态资源或运行时数据
```

## 4. 创建 Python 包入口 `app/__init__.py`

我添加了：

```text
app/__init__.py
```

这个文件是空的，但它有一个重要作用：告诉 Python，`app` 是一个可以被导入的包。

如果没有它，某些 Python 环境或工具在执行：

```python
from app.main import app
```

时可能会出现导入问题。

前端类比：它有点像让一个目录成为模块边界，只不过 JavaScript/TypeScript 不需要通过空文件来声明。

## 5. 创建接口返回结构 `app/schemas.py`

我创建了：

```text
app/schemas.py
```

里面定义了两个 Pydantic 模型：

```python
class HealthResp(BaseModel):
    status: str = "ok"
    app: str
    env: str


class HelloResp(BaseModel):
    message: str
```

这里的 `BaseModel` 来自 Pydantic。你可以把它理解成：

```ts
type HealthResp = {
  status: string
  app: string
  env: string
}

type HelloResp = {
  message: string
}
```

但 Pydantic 不只是类型声明，它还可以做运行时数据校验、默认值处理和序列化。

前端里 TypeScript 的类型在运行后会被擦除；Pydantic 的模型在 Python 运行时仍然存在，所以后端接口可以真正校验和整理数据。

## 6. 创建未来知识库数据模型 `app/models.py`

我创建了：

```text
app/models.py
```

里面定义了：

```python
@dataclass
class DocumentChunk:
    doc_id: str
    chunk_id: str
    text: str
    source: str | None = None
```

这个类目前只是占位。它表示未来知识库系统里的一段文档切片。

字段含义：

```text
doc_id    原始文档 ID
chunk_id  文档切片 ID
text      切片文本
source    来源，可选
```

为什么知识库需要 chunk？

因为 AI 知识库通常不会把一整篇文档一次性塞给大模型，而是先把文档切成小块，再根据用户问题检索最相关的块，最后把相关内容交给模型回答。

这属于后续 RAG，也就是 Retrieval-Augmented Generation，检索增强生成。

## 7. 创建 ingest 占位脚本 `app/ingest.py`

我创建了：

```text
app/ingest.py
```

里面有一个简单函数：

```python
def run(path: str = "data") -> None:
    p = Path(path)
    print(f"[ingest] placeholder: future file processing will run under {p.resolve()}")
```

它现在不会真正处理文件，只会打印未来处理文件的位置。

这个文件的意义是提前留好入口，后续可以在这里加入：

1. 读取 PDF、Markdown、TXT。
2. 切分文档。
3. 生成 embedding。
4. 写入向量数据库。

前端类比：这有点像你先创建一个 `services/upload.ts` 或 `utils/parser.ts`，第一周先留接口，第二周再补完整逻辑。

我也验证过这个脚本可以运行：

```bash
.venv/bin/python -m app.ingest
```

输出类似：

```text
[ingest] placeholder: future file processing will run under /root/my/ai-knowledge-copilot/data
```

## 8. 创建 FastAPI 主应用 `app/main.py`

这是本次最核心的文件：

```text
app/main.py
```

它负责创建 Web 服务、读取配置、注册中间件和定义接口。

### 8.1 导入依赖

文件开头导入了这些模块：

```python
import asyncio
import json
import logging
import time
import uuid
```

它们分别用于：

```text
asyncio   处理异步等待，SSE 流式接口会用到
json      把 Python 字典转成 JSON 字符串
logging   输出日志
time      统计请求耗时
uuid      给每个请求生成唯一 request id
```

然后导入 FastAPI 相关能力：

```python
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
```

前端类比：

```text
FastAPI             类似 Express、Koa、NestJS 的服务实例
Query               声明和校验 URL query 参数
Request             当前 HTTP 请求对象
CORSMiddleware      处理跨域
JSONResponse        手动返回 JSON 响应
StreamingResponse   返回流式响应
```

### 8.2 定义配置类 `Settings`

我定义了：

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "ai-knowledge-copilot"
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    STREAM_DELAY_SECONDS: float = 1.0
```

这表示应用配置可以从 `.env` 文件读取。

前端类比：

```text
.env
VITE_API_BASE_URL=...
NEXT_PUBLIC_API_URL=...
```

Python 后端里同样不应该把配置和密钥写死在代码里，尤其是后续接 OpenAI API Key 时。

### 8.3 初始化日志

我配置了基础日志：

```python
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
)
```

这样每次请求时，服务可以输出路径、状态码、耗时和 request id。

后端日志的意义很大。前端出问题时你会看浏览器 console、Network 面板；后端出问题时主要看日志。

### 8.4 创建 FastAPI 应用

```python
app = FastAPI(title=settings.APP_NAME)
```

这一行创建了 FastAPI 应用实例。

`title` 会显示在自动生成的接口文档里。

FastAPI 会自动生成：

```text
/docs
/openapi.json
```

`/docs` 是 Swagger UI，可以直接在浏览器里调接口。

### 8.5 添加 CORS 中间件

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.CORS_ORIGINS.split(",") if x.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

CORS 是前端非常熟悉的问题：浏览器不允许一个来源随便请求另一个来源。

例如：

```text
前端: http://localhost:3000
后端: http://127.0.0.1:8000
```

这两个 origin 不同，如果后端不允许跨域，浏览器会拦截请求。

这里允许的前端来源来自 `.env`：

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 9. 添加请求日志中间件

我添加了：

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled path=%s rid=%s", request.url.path, request_id)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "request_id": request_id},
        )

    response.headers["X-Request-Id"] = request_id
    logger.info(...)
    return response
```

这个中间件做了几件事：

1. 每个请求生成一个唯一 request id。
2. 记录请求开始时间。
3. 调用真正的接口处理函数。
4. 如果接口报错，返回统一的 500 JSON。
5. 给响应头加上 `X-Request-Id`。
6. 输出请求路径、状态码、耗时。

前端类比：这类似 Axios interceptor 或 Next.js middleware，只不过它运行在服务端。

为什么要有 request id？

当前端报错时，你可以把响应头里的 `X-Request-Id` 发给后端，后端就可以在日志里查到同一次请求。

## 10. 实现 `/health` 接口

代码：

```python
@app.get("/health", response_model=HealthResp)
async def health() -> HealthResp:
    return HealthResp(app=settings.APP_NAME, env=settings.APP_ENV)
```

作用：

```text
检查服务是否活着
```

返回：

```json
{
  "status": "ok",
  "app": "ai-knowledge-copilot",
  "env": "dev"
}
```

`response_model=HealthResp` 表示这个接口的响应结构要符合 `HealthResp`。

前端类比：相当于给接口响应加了类型约束和文档声明。

## 11. 实现 `/hello` 接口

代码：

```python
@app.get("/hello", response_model=HelloResp)
async def hello(name: str = Query("world", min_length=1, max_length=50)) -> HelloResp:
    return HelloResp(message=f"Hello, {name}")
```

访问：

```text
/hello?name=FE
```

返回：

```json
{
  "message": "Hello, FE"
}
```

这里的 `Query` 做了参数约束：

```text
默认值: world
最短长度: 1
最长长度: 50
```

如果你传一个空字符串或过长字符串，FastAPI 会自动返回参数校验错误。

前端类比：类似你用 Zod 校验 URL query，只不过这里发生在后端。

## 12. 实现 `/stream` SSE 流式接口

代码核心是：

```python
async def event_gen(delay_seconds: float | None = None) -> AsyncGenerator[str, None]:
    delay = settings.STREAM_DELAY_SECONDS if delay_seconds is None else delay_seconds
    for i in range(1, 6):
        payload = {"token": f"chunk-{i}"}
        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        await asyncio.sleep(delay)
```

它会依次输出 5 个事件：

```text
data: {"token": "chunk-1"}

data: {"token": "chunk-2"}

...
```

接口：

```python
@app.get("/stream")
async def stream() -> StreamingResponse:
    return StreamingResponse(event_gen(), media_type="text/event-stream")
```

这里使用的是 SSE，也就是 Server-Sent Events。

前端可以这样接：

```ts
const es = new EventSource("http://127.0.0.1:8000/stream")

es.onmessage = (event) => {
  console.log(JSON.parse(event.data))
}
```

为什么 AI 项目需要流式接口？

因为大模型回答通常不是一次性返回完整文本，而是一个 token 一个 token 地生成。ChatGPT 那种“字逐渐出现”的效果，本质上就是流式返回。

本周的 `/stream` 是最小版模拟：

```text
chunk-1
chunk-2
chunk-3
chunk-4
chunk-5
```

后续可以把它替换成真实的大模型流式输出。

## 13. 创建依赖文件 `requirements.txt`

我创建了：

```text
requirements.txt
```

当前内容是：

```txt
fastapi[standard]>=0.115,<0.116
starlette>=0.40,<0.47
pydantic-settings
python-dotenv
pytest
httpx
```

它的作用类似前端的 `package.json` 依赖列表。

各依赖作用：

```text
fastapi[standard]  FastAPI Web 框架和常用运行依赖
starlette          FastAPI 底层使用的 ASGI 框架
pydantic-settings  从 .env 读取配置
python-dotenv      支持 .env 文件
pytest             Python 测试框架
httpx              HTTP 客户端，测试接口时使用
```

我没有简单写成：

```txt
fastapi[standard]
```

而是固定了版本范围：

```txt
fastapi[standard]>=0.115,<0.116
starlette>=0.40,<0.47
```

原因是第一次安装时，默认解析到了更新的 FastAPI/Starlette 组合，在当前执行环境里测试请求会卡住。固定到成熟稳定的版本组合后，接口和测试都可以正常运行。

前端类比：这类似你在 `package.json` 里锁定某个 React、Vite 或 Next.js 版本范围，避免新版本 breaking change 影响学习项目。

## 14. 创建环境变量文件

我创建了两个文件：

```text
.env.example
.env
```

`.env.example` 是模板，可以提交到仓库。

`.env` 是本地真实配置，不应该提交真实密钥。

内容：

```env
APP_NAME=ai-knowledge-copilot
APP_ENV=dev
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
STREAM_DELAY_SECONDS=1
OPENAI_API_KEY=
```

字段含义：

```text
APP_NAME              应用名
APP_ENV               当前环境
LOG_LEVEL             日志等级
CORS_ORIGINS          允许跨域访问的前端地址
STREAM_DELAY_SECONDS  每个 SSE chunk 之间等待几秒
OPENAI_API_KEY        未来调用 OpenAI API 时使用
```

`OPENAI_API_KEY` 现在为空，因为 Week1 不真正调用模型。

安全习惯：API Key 不要写死在代码里，也不要提交到 Git。

## 15. 创建 `.gitignore`

我创建了：

```text
.gitignore
```

内容包括：

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
*.py[cod]
```

它的作用是避免把这些文件提交到 Git：

```text
.env           本地密钥和配置
.venv/         Python 虚拟环境
__pycache__/   Python 编译缓存
.pytest_cache/ pytest 缓存
*.pyc          Python 字节码文件
```

前端类比：

```gitignore
.env.local
node_modules/
dist/
.next/
```

## 16. 创建测试文件 `tests/test_main.py`

我创建了：

```text
tests/test_main.py
```

里面测试了 3 个接口：

```text
test_health        测试 /health
test_hello         测试 /hello
test_stream_events 测试 /stream
```

最终测试命令是：

```bash
.venv/bin/python -m pytest -q
```

测试结果：

```text
3 passed in 0.23s
```

### 为什么测试里用了 `httpx.ASGITransport`

一开始按常见写法使用了：

```python
from fastapi.testclient import TestClient
```

但在当前运行环境里，同步 `TestClient` 请求会卡住。

我改成了：

```python
transport = httpx.ASGITransport(app=app)
async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
    yield c
```

这表示不真正启动一个 HTTP 服务器，而是直接把请求送进 FastAPI 应用。

好处：

1. 测试更快。
2. 不占用端口。
3. 适合测试异步接口。
4. 避免当前环境里 `TestClient` 的同步路径卡住。

前端类比：类似你测试 React 组件时不真的启动浏览器服务，而是用测试工具直接渲染组件并断言结果。

## 17. 创建 docker/Dockerfile

我创建了：

```text
docker/Dockerfile
```

内容做了这些事：

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY tests ./tests
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

逐行解释：

```text
FROM python:3.11-slim
使用 Python 3.11 的轻量镜像。

WORKDIR /app
容器内工作目录设为 /app。

COPY requirements.txt .
先复制依赖文件。

RUN pip install --no-cache-dir -r requirements.txt
安装 Python 依赖。

COPY app ./app
COPY tests ./tests
复制应用代码和测试代码。

EXPOSE 8000
声明容器监听 8000 端口。

CMD [...]
容器启动时运行 Uvicorn 服务。
```

前端类比：类似给一个 Node 服务写 docker/Dockerfile，只不过基础镜像从 `node` 换成了 `python`。

## 18. 创建 `docker-compose.yml`

我创建了：

```text
docker-compose.yml
```

内容：

```yaml
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

作用：

```text
build: .       使用当前目录的 docker/Dockerfile 构建镜像
command        开发模式启动服务
ports          把容器 8000 端口映射到本机 8000
env_file       读取 .env 配置
volumes        把本地目录挂载进容器，方便热更新
```

我检查过当前环境没有 `docker` 命令，所以没有实际运行：

```bash
docker compose up --build
```

但 Docker 相关文件已经生成好，在安装 Docker 的机器上可以使用。

## 19. 创建 README

我创建了：

```text
README.md
```

它说明了：

1. 项目是什么。
2. 如何创建虚拟环境。
3. 如何安装依赖。
4. 如何启动服务。
5. 本地有哪些接口。
6. 如何运行测试。
7. 如何用 Docker 启动。
8. 常见问题。

README 是给“下一个接手项目的人”看的。即使下一个人就是未来的你，也应该写清楚。

## 20. 创建 Python 虚拟环境 `.venv`

我执行了：

```bash
python3.11 -m venv .venv
```

这会创建一个本地虚拟环境：

```text
.venv/
```

Python 虚拟环境的作用类似前端的 `node_modules` 加项目级 Node 版本隔离。

为什么需要虚拟环境？

如果你把所有 Python 包都安装到系统 Python 里，不同项目之间会互相污染。例如一个项目需要 FastAPI 0.115，另一个项目需要 0.136，就可能冲突。

使用 `.venv` 后，本项目依赖只安装在当前项目目录下。

之后运行 Python 命令时，我使用：

```bash
.venv/bin/python
```

而不是系统的：

```bash
python
```

这样可以确保使用的是项目自己的 Python 环境。

## 21. 安装依赖

我执行了：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

第一次在普通沙箱里安装时，网络被限制，无法访问 Python 包索引。

之后我使用了允许联网的执行方式重新安装，依赖安装成功。

这一步类似前端执行：

```bash
npm install
```

或：

```bash
pnpm install
```

Python 里 `pip` 就是最常见的包安装工具。

## 22. 处理依赖版本和测试卡住问题

安装依赖后，我先运行：

```bash
.venv/bin/python -m pytest -q
```

发现测试没有及时返回。

我进一步做了几个最小验证：

1. 测试 FastAPI 的 `TestClient`。
2. 测试 Starlette 原生 ASGI 应用。
3. 测试 `httpx.ASGITransport`。
4. 测试真实的 `app.main`。

结论是：

1. 默认解析到的最新 FastAPI/Starlette 组合在当前环境里不稳定。
2. 同步 `TestClient` 在当前执行环境里会卡住。
3. 异步 `httpx.ASGITransport` 可以正常测试我们的 FastAPI app。

所以我做了两件修正：

```txt
fastapi[standard]>=0.115,<0.116
starlette>=0.40,<0.47
```

并把测试改成异步 HTTP 客户端。

这是工程里很常见的排障过程：不是看到报错就盲改，而是先缩小范围，找到是业务代码、测试工具、依赖版本还是运行环境的问题。

## 23. 运行测试并通过

最终测试命令：

```bash
.venv/bin/python -m pytest -q
```

结果：

```text
...                                                                      [100%]
3 passed in 0.23s
```

这表示：

```text
/health 测试通过
/hello  测试通过
/stream 测试通过
```

前端类比：类似 Vitest 或 Jest 输出所有测试通过。

## 24. 启动本地服务并验证接口

我启动服务使用的是：

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

这里的 `uvicorn` 是 ASGI 服务器。

你可以理解为：

```text
FastAPI 负责定义应用和路由
Uvicorn 负责真正监听端口并处理 HTTP 请求
```

前端类比：

```text
Vite dev server 负责启动本地前端服务
Uvicorn 负责启动本地 Python 后端服务
```

验证结果：

```text
GET /health
{"status":"ok","app":"ai-knowledge-copilot","env":"dev"}
```

```text
GET /hello?name=FE
{"message":"Hello, FE"}
```

```text
GET /stream
data: {"token": "chunk-1"}

data: {"token": "chunk-2"}

data: {"token": "chunk-3"}

data: {"token": "chunk-4"}

data: {"token": "chunk-5"}
```

## 25. 处理本地 curl 代理和沙箱网络问题

第一次用 `curl` 验证接口时，当前 shell 里有代理配置，`curl` 被转发到了代理端口，导致连接失败。

我改用了：

```bash
curl --noproxy '*'
```

后来又发现不同命令之间存在沙箱网络隔离，所以我用允许本地网络访问的方式启动服务并验证接口。

这不是应用代码问题，而是执行环境限制。

实际本地开发时，你通常只需要：

```bash
uvicorn app.main:app --reload
```

然后浏览器访问：

```text
http://127.0.0.1:8000/docs
```

## 26. 最终项目文件结构

当前核心文件如下：

```text
ai-knowledge-copilot/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ schemas.py
│  ├─ models.py
│  └─ ingest.py
├─ tests/
│  └─ test_main.py
├─ data/
├─ .env
├─ .env.example
├─ .gitignore
├─ requirements.txt
├─ docker/Dockerfile
├─ docker-compose.yml
├─ README.md
├─ docs/weeks/week-01/claude-code-summary.md
└─ docs/weeks/week-01/prompt.md
```

## 27. 你现在可以怎么运行

如果当前 `.venv` 已经存在，可以直接：

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

然后访问：

```text
http://127.0.0.1:8000/docs
```

测试：

```bash
pytest -q
```

如果是新机器，从零开始：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 28. 前端开发者需要重点理解的 Python 概念

### 虚拟环境

```text
Python .venv ~= 前端项目自己的 node_modules 和运行环境隔离
```

### requirements.txt

```text
requirements.txt ~= package.json 的 dependencies 部分
```

但它没有 scripts、devDependencies 等完整功能，只是依赖列表。

### pip

```text
pip ~= npm / pnpm / yarn
```

### FastAPI

```text
FastAPI ~= Express / Koa / NestJS
```

它是 Web API 框架。

### Uvicorn

```text
Uvicorn ~= dev server / HTTP server
```

它负责监听端口，把 HTTP 请求交给 FastAPI。

### Pydantic

```text
Pydantic ~= TypeScript 类型 + Zod 运行时校验
```

但它主要运行在 Python 后端。

### pytest

```text
pytest ~= Jest / Vitest
```

### async / await

Python 也有 `async` / `await`，概念和 JavaScript 很像，但运行时模型、事件循环和线程池细节不同。

### SSE

```text
SSE ~= EventSource 接收服务端连续推送消息
```

它适合 AI token 流式输出。

## 29. 和 AI 学习路线的关系

这次 Week1 还没有真正接入大模型，但已经搭好了 AI 应用的基础设施：

```text
FastAPI 服务             后续承载 AI 接口
/stream                  后续承载模型流式输出
.env / OPENAI_API_KEY    后续安全读取模型密钥
data/                    后续存放知识库文件
DocumentChunk            后续表示文档切片
ingest.py                后续处理文档入库
pytest                   保证后续改动不破坏基础接口
docker/Dockerfile               后续部署服务
```

AI 应用不是只写一个模型调用。真实项目通常需要：

1. Web API。
2. 配置和密钥管理。
3. 日志和错误处理。
4. 流式响应。
5. 文件处理。
6. 向量检索。
7. 测试。
8. 部署。

Week1 做的是最小但完整的后端底座。

## 30. 本次任务最终结果

已完成：

```text
FastAPI 基础服务
/health 接口
/hello 接口
/stream SSE 接口
Pydantic 响应模型
.env 配置读取
CORS 配置
请求日志中间件
测试用例
虚拟环境
依赖安装
README
docker/Dockerfile
docker-compose.yml
ingest 占位脚本
data 目录
```

已验证：

```text
pytest -q 通过
本地 HTTP 接口通过
SSE 流式输出通过
ingest 占位脚本可运行
```

未能验证：

```text
docker compose up --build
```

原因是当前环境没有安装 `docker` 命令，不是项目文件缺失。

