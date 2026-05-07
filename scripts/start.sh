#!/bin/bash

# LangMentor 本地启动脚本
set -e

cd "$(dirname "$0")/.."
BASE_DIR=$(pwd)

# 环境变量
export SERVICE_NAME=api-gateway
export RABBITMQ_URL=amqp://admin:admin123@localhost:5672/
export REDIS_URL=redis://localhost:6379/0
export DATABASE_URL=mysql+pymysql://langmentor_user:langmentor_pass@localhost:3306/langmentor_db
export RAG_SERVICE_URL=http://localhost:8081
export LLM_SERVICE_URL=http://localhost:8082
export CHROMA_HOST=localhost
export CHROMA_PORT=8000
export CELERY_BROKER_URL=amqp://admin:admin123@localhost:5672/
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
export OPENAI_API_KEY=${OPENAI_API_KEY:-}
export PYTHONPATH="$BASE_DIR/backend:$PYTHONPATH"

echo "========================================="
echo "  LangMentor 本地服务启动脚本"
echo "========================================="
echo ""

# 检查基础设施
echo "检查 Docker 基础设施服务..."
if ! docker ps | grep -q langmentor-rabbitmq; then
    echo "启动基础设施服务..."
    docker-compose up -d rabbitmq redis mysql chroma
    sleep 10
fi
echo "基础设施服务已就绪"
echo ""

# 激活虚拟环境
source "$BASE_DIR/backend/venv/bin/activate"

# 启动 RAG Service
echo "启动 RAG Service (http://localhost:8081)..."
cd "$BASE_DIR/backend"
nohup python -m uvicorn rag-service.app.main:app --host 0.0.0.0 --port 8081 --reload > "$BASE_DIR/logs/rag-service.log" 2>&1 &
echo $! > "$BASE_DIR/logs/rag-service.pid"
sleep 2

# 启动 LLM Service
echo "启动 LLM Service (http://localhost:8082)..."
nohup python -m uvicorn llm-service.app.main:app --host 0.0.0.0 --port 8082 --reload > "$BASE_DIR/logs/llm-service.log" 2>&1 &
echo $! > "$BASE_DIR/logs/llm-service.pid"
sleep 2

# 启动 API Gateway
echo "启动 API Gateway (http://localhost:8080)..."
nohup python -m uvicorn api-gateway.app.main:app --host 0.0.0.0 --port 8080 --reload > "$BASE_DIR/logs/api-gateway.log" 2>&1 &
echo $! > "$BASE_DIR/logs/api-gateway.pid"
sleep 2

# 启动 Celery Worker
echo "启动 Celery Worker..."
cd "$BASE_DIR/backend"
nohup celery -A celery-worker.tasks worker --loglevel=info --concurrency=2 > "$BASE_DIR/logs/celery-worker.log" 2>&1 &
echo $! > "$BASE_DIR/logs/celery-worker.pid"

# 启动 Frontend
echo "启动 Frontend (http://localhost:3000)..."
cd "$BASE_DIR/frontend"
nohup npm run dev > "$BASE_DIR/logs/frontend.log" 2>&1 &
echo $! > "$BASE_DIR/logs/frontend.pid"

echo ""
echo "========================================="
echo "  所有服务已启动!"
echo "========================================="
echo ""
echo "访问地址:"
echo "  前端:        http://localhost:3000"
echo "  API 网关:    http://localhost:8080"
echo "  RAG 服务:    http://localhost:8081"
echo "  LLM 服务:    http://localhost:8082"
echo "  RabbitMQ:    http://localhost:15672 (admin/admin123)"
echo "  Celery:      http://localhost:5555"
echo ""
echo "查看日志: tail -f logs/*.log"
echo "停止服务: ./scripts/stop.sh"
echo ""
