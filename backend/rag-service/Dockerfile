FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY README.md .

RUN uv pip install --system -e "."

COPY rag-service/ ./rag-service/
COPY shared/ ./shared/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "rag-service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
