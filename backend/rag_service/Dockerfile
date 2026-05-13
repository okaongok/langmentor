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

COPY rag-service/ ./rag_service/
COPY shared/ ./shared/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "rag_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
