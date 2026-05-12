#!/bin/bash

# LangMentor 高可用部署脚本
# 使用 Docker Swarm 模式

set -e

cd "$(dirname "$0")/.."
BASE_DIR=$(pwd)

echo "========================================="
echo "  LangMentor 高可用部署"
echo "========================================="
echo ""

# 检查 Docker Swarm 模式
if ! docker info | grep -q "Swarm: active"; then
    echo "初始化 Docker Swarm..."
    docker swarm init --advertise-addr 127.0.0.1 || true
fi

# 创建网络
echo "创建 overlay 网络..."
docker network create --driver overlay --attachable langmentor-net 2>/dev/null || true

# 部署基础设施
echo "部署基础设施服务..."
docker stack deploy -c docker-compose.infra.yml langmentor-infra

# 等待基础设施就绪
echo "等待基础设施就绪..."
sleep 15

# 部署应用服务
echo "部署应用服务..."
docker stack deploy -c docker-compose.ha.yml langmentor

# 部署监控
echo "部署监控系统..."
docker stack deploy -c docker-compose.monitoring.yml langmentor-mon

echo ""
echo "========================================="
echo "  高可用部署完成!"
echo "========================================="
echo ""
echo "访问地址:"
echo "  前端:        http://localhost"
echo "  API 网关:    http://localhost/api"
echo "  Grafana:     http://localhost:3001"
echo "  Prometheus:  http://localhost:9090"
echo "  RabbitMQ:    http://localhost:15672"
echo "  Flower:      http://localhost:5555"
echo ""
echo "查看服务状态: docker service ls"
echo "查看日志: docker service logs langmentor_api-gateway"
echo ""
