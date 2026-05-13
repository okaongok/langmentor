from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
import signal
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from shared.models.base import SessionLocal, ChatSession, ChatMessage


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down API Gateway...")


app = FastAPI(title="LangMentor API Gateway", version="0.1.0", lifespan=lifespan)

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


class SessionListItem(BaseModel):
    id: str
    title: Optional[str]
    created_at: str
    updated_at: str
    message_count: int


class MessageItem(BaseModel):
    role: str
    content: str


class SessionDetail(BaseModel):
    session_id: str
    messages: List[MessageItem]


def _get_db():
    return SessionLocal()


@app.get("/health")
async def health_check():
    health = {"status": "healthy", "service": "api-gateway", "dependencies": {}}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LLM_SERVICE_URL}/health", timeout=2.0)
            health["dependencies"]["llm"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health["dependencies"]["llm"] = "unreachable"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RAG_SERVICE_URL}/health", timeout=2.0)
            health["dependencies"]["rag"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health["dependencies"]["rag"] = "unreachable"

    return health


@app.get("/api/sessions", response_model=List[SessionListItem])
async def list_sessions(user_id: str = "anonymous"):
    db = _get_db()
    try:
        from sqlalchemy import or_
        sessions = db.query(ChatSession).filter(
            or_(ChatSession.user_id == user_id, ChatSession.user_id.is_(None))
        ).order_by(ChatSession.updated_at.desc()).all()
        result = []
        for s in sessions:
            result.append(SessionListItem(
                id=s.id,
                title=s.title or f"会话 {s.created_at.strftime('%m-%d %H:%M')}",
                created_at=s.created_at.isoformat(),
                updated_at=s.updated_at.isoformat(),
                message_count=len(s.messages)
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/api/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LLM_SERVICE_URL}/sessions/{session_id}",
                timeout=5.0
            )
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Session not found")
            data = response.json()
            return SessionDetail(
                session_id=data["session_id"],
                messages=[MessageItem(role=m["role"], content=m["content"]) for m in data["messages"]]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    db = _get_db()
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        db.delete(session)
        db.commit()
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        async with httpx.AsyncClient() as client:
            rag_response = await client.post(
                f"{RAG_SERVICE_URL}/retrieve",
                json={"query": request.message, "top_k": 3},
                timeout=30.0
            )
            context = rag_response.json().get("results", [])

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


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        try:
            async with httpx.AsyncClient() as client:
                rag_response = await client.post(
                    f"{RAG_SERVICE_URL}/retrieve",
                    json={"query": request.message, "top_k": 3},
                    timeout=30.0
                )
                context = rag_response.json().get("results", [])

                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        f"{LLM_SERVICE_URL}/generate/stream",
                        json={
                            "message": request.message,
                            "context": context,
                            "session_id": request.session_id,
                        },
                        timeout=60.0
                    ) as response:
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                yield line + "\n\n"

        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


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
