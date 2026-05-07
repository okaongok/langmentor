#!/bin/bash

# LangMentor 停止脚本

cd "$(dirname "$0")/.."
BASE_DIR=$(pwd)

echo "停止 LangMentor 服务..."

# 停止 Python 服务
for service in api-gateway rag-service llm-service celery-worker; do
    pid_file="$BASE_DIR/logs/${service}.pid"
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "停止 $service (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
        fi
        rm -f "$pid_file"
    fi
done

# 停止 Frontend
pid_file="$BASE_DIR/logs/frontend.pid"
if [ -f "$pid_file" ]; then
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        echo "停止 frontend (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
fi

echo "服务已停止"
echo "如需停止基础设施: docker-compose down"
