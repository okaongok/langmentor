# LangMentor

LangMentor 是一个 AI 语言学习助手 MVP，采用前后端分离架构，集成了现代 AI 技术栈。

## 技术栈

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **Celery** - 分布式任务队列
- **RabbitMQ** - 消息代理
- **Redis** - 缓存和结果后端
- **MySQL** - 关系型数据库
- **ChromaDB** - 向量数据库
- **LangChain** - LLM 应用框架
- **OpenAI** - 大语言模型

### 前端
- **Next.js 14** - React 框架
- **Tailwind CSS** - 原子化 CSS
- **TypeScript** - 类型安全

### 基础设施
- **Docker** - 容器化
- **Docker Compose** - 多服务编排
- **UV** - Python 包管理

## 项目结构

```
langmentor/
├── frontend/           # Next.js 前端
│   ├── app/           # App Router
│   ├── components/    # React 组件
│   ├── lib/           # 工具函数
│   └── public/        # 静态资源
├── backend/           # FastAPI 后端
│   ├── api-gateway/   # API 网关
│   ├── rag-service/   # RAG 检索服务
│   ├── llm-service/   # LLM 生成服务
│   ├── celery-worker/ # Celery 任务队列
│   ├── shared/        # 共享模块
│   └── scripts/       # 数据库脚本
├── docker-compose.yml # Docker 编排
└── .env.example       # 环境变量模板
```

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key
```

### 2. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 访问服务

- **前端**: http://localhost:3000
- **API 网关**: http://localhost:8080
- **RAG 服务**: http://localhost:8081
- **LLM 服务**: http://localhost:8082
- **RabbitMQ 管理**: http://localhost:15672 (admin/admin123)
- **Celery Flower**: http://localhost:5555

## 使用 UV 管理依赖

```bash
# 安装 uv
pip install uv

# 安装项目依赖
cd backend
uv pip install -e "."

# 运行开发服务器
uvicorn api-gateway.app.main:app --reload
```

## 功能特性

- [x] 智能对话（基于 LLM）
- [x] RAG 知识检索
- [x] 文档管理
- [x] 异步任务处理
- [x] 微服务架构
- [x] Docker 容器化

## 开发

### 添加新文档到知识库

```bash
curl -X POST http://localhost:8080/api/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "示例文档", "content": "文档内容...", "source": "manual"}'
```

### 对话

前端已集成对话界面，直接访问 http://localhost:3000 即可使用。

## 许可证

MIT
