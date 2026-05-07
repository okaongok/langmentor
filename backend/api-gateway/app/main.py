from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="LangMentor API Gateway", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8081")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8082")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str | None = None


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        async with httpx.AsyncClient() as client:
            # 先调用 RAG 服务检索相关知识
            rag_response = await client.post(
                f"{RAG_SERVICE_URL}/retrieve",
                json={"query": request.message, "top_k": 3},
                timeout=30.0
            )
            context = rag_response.json().get("results", [])

            # 再调用 LLM 服务生成回复
            llm_response = await client.post(
                f"{LLM_SERVICE_URL}/generate",
                json={
                    "message": request.message,
                    "context": context,
                    "session_id": request.session_id,
                },
                timeout=60.0
            )
            result = llm_response.json()

            return ChatResponse(
                response=result.get("response", ""),
                session_id=result.get("session_id"),
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents")
async def create_document(title: str, content: str, source: str = ""):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RAG_SERVICE_URL}/documents",
                json={"title": title, "content": content, "source": source},
                timeout=30.0
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RAG_SERVICE_URL}/documents",
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
