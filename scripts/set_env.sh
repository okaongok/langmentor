#!/bin/bash

# LangMentor 本地启动脚本
# 基础设施已通过 Docker Compose 启动

cd "$(dirname "$0")"

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

echo "环境变量已设置"
echo "RAG_SERVICE_URL=$RAG_SERVICE_URL"
echo "LLM_SERVICE_URL=$LLM_SERVICE_URL"
echo "RABBITMQ_URL=$RABBITMQ_URL"
echo "REDIS_URL=$REDIS_URL"
