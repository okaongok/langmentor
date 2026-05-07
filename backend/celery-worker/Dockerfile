FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY README.md .

RUN uv pip install --system -e "."

COPY celery-worker/ ./celery-worker/
COPY shared/ ./shared/
COPY rag-service/ ./rag-service/
COPY llm-service/ ./llm-service/

ENV PYTHONPATH=/app

CMD ["celery", "-A", "celery-worker.tasks", "worker", "--loglevel=info", "--concurrency=2"]
