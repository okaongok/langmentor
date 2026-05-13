FROM python:3.11-slim

WORKDIR /app

# 使用国内pip镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
COPY pyproject.toml .
COPY README.md .

# 先安装build工具
RUN pip install --no-cache-dir hatchling

# 安装所有依赖（使用pip而不是uv，更稳定）
RUN pip install --no-cache-dir \
    fastapi uvicorn[standard] celery redis pika \
    sqlalchemy pymysql aiomysql alembic \
    langchain langchain-openai langchain-community \
    chromadb openai \
    pydantic pydantic-settings python-dotenv httpx \
    pytest pytest-asyncio black isort flake8 mypy flower

# 复制代码到Python兼容的目录名（使用下划线）
COPY api-gateway/ ./api_gateway/
COPY shared/ ./shared/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api_gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
