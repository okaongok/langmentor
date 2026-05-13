FROM python:3.11-slim

WORKDIR /app

# 使用国内pip镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
COPY pyproject.toml .
COPY README.md .

RUN pip install --no-cache-dir hatchling

RUN pip install --no-cache-dir \
    fastapi uvicorn[standard] celery redis pika \
    sqlalchemy pymysql aiomysql alembic \
    langchain langchain-openai langchain-community \
    chromadb openai \
    pydantic pydantic-settings python-dotenv httpx \
    pytest pytest-asyncio black isort flake8 mypy flower

COPY celery-worker/ ./celery_worker/
COPY shared/ ./shared/
COPY rag-service/ ./rag_service/
COPY llm-service/ ./llm_service/

ENV PYTHONPATH=/app

CMD ["celery", "-A", "celery_worker.tasks", "worker", "--loglevel=info", "--concurrency=2"]
