# LangMentor Dev Commands
# ──────────────────────────────────────────────────────────
# just                   → 列出所有命令
# just dev               → 一键启动全部
# just dev-backend       → 启动后端三个服务
# just dev-frontend      → 启动前端
# just infra-up          → 启动基础设施

set shell := ["bash", "-c"]

project_root := "."
backend_dir := project_root / "backend"
frontend_dir := project_root / "frontend"
env_file := justfile_directory() / ".env.development"

# ─── 配方 ─────────────────────────────────────────────────

# 显示所有命令
_default:
    @just --list

# 一键启动全部（基础设施 + 后端 + 前端 + Celery Worker）
dev: infra-up
    @echo "─── 启动后端服务 ───"
    @just _run_service "api_gateway"   "api_gateway"   "8080"  "API Gateway" &
    @just _run_service "llm_service"   "llm_service"   "8082"  "LLM Service" &
    @just _run_service "rag_service"   "rag_service"   "8081"  "RAG Service" &
    @echo "  → Celery Worker"
    @cd {{backend_dir}} && source .venv/bin/activate && PYTHONPATH={{backend_dir}} eval $(grep -v '^#' {{env_file}} | xargs) celery -A celery_worker.config worker --loglevel=info &
    @echo "─── 启动前端 ───"
    cd {{frontend_dir}} && npm run dev

# 启动后端全部三个微服务 + Celery Worker（后台）
dev-backend:
    @echo "─── 启动后端服务 ───"
    @just _run_service "api_gateway"   "api_gateway"   "8080"  "API Gateway" &
    @just _run_service "llm_service"   "llm_service"   "8082"  "LLM Service" &
    @just _run_service "rag_service"   "rag_service"   "8081"  "RAG Service" &
    @echo "  → Celery Worker"
    @cd {{backend_dir}} && source .venv/bin/activate && PYTHONPATH={{backend_dir}} eval $(grep -v '^#' {{env_file}} | xargs) celery -A celery_worker.config worker --loglevel=info &

# 启动前端
dev-frontend:
    @echo "─── 启动前端 ───"
    cd {{frontend_dir}} && npm run dev

# 启动基础设施（Docker）
infra-up:
    @echo "─── 启动 Docker 基础设施 ───"
    docker compose up -d mysql redis rabbitmq chroma 2>&1 | tail -1

# 停止所有服务
stop:
    @echo "─── 停止所有服务 ───"
    @pkill -f "uvicorn api_gateway" 2>/dev/null || true
    @pkill -f "uvicorn llm_service" 2>/dev/null || true
    @pkill -f "uvicorn rag_service" 2>/dev/null || true
    @pkill -f "celery -A celery_worker" 2>/dev/null || true
    @echo "✓ 后端服务已停止"

# 停止基础设施
infra-down:
    @echo "─── 停止 Docker 基础设施 ───"
    docker compose down

# 安装所有依赖
deps: _deps-python _deps-frontend
    @echo "✓ 所有依赖安装完成"

_deps-python:
    @echo "─── 安装 Python 依赖 ───"
    cd {{backend_dir}} && uv venv && uv pip install \
        fastapi uvicorn[standard] celery redis pika \
        sqlalchemy pymysql aiomysql alembic \
        langchain langchain-openai langchain-community langchain-chroma \
        chromadb openai \
        pydantic pydantic-settings python-dotenv httpx \
        pytest pytest-asyncio black isort flake8 mypy flower

_deps-frontend:
    @echo "─── 安装前端依赖 ───"
    cd {{frontend_dir}} && npm install

# 初始化开发环境
setup:
    @just deps
    @echo ""
    @echo "┌─────────────────────────────────────────┐"
    @echo "│  开发环境已就绪，运行 just dev 启动服务   │"
    @echo "└─────────────────────────────────────────┘"

# 内部：运行一个 uvicorn 服务
_run_service module dir port label:
    @echo "  → {{label}}  http://localhost:{{port}}"
    cd {{backend_dir}} && \
    source .venv/bin/activate && \
    PYTHONPATH={{backend_dir}} \
    eval $(grep -v '^#' {{env_file}} | xargs) \
    uvicorn {{module}}.app.main:app --host 0.0.0.0 --port {{port}} --reload
