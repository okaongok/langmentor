from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Generator
import os
import json
import asyncio
import redis
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import message_to_dict, messages_from_dict
from langchain_core.tools import tool
from langchain.agents import create_agent
from celery_worker.tasks import persist_chat_session
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down LLM Service...")


app = FastAPI(title="LangMentor LLM Service", version="0.1.0", lifespan=lifespan)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

llm = None
agent = None

redis_client = redis.from_url(REDIS_URL, decode_responses=True)
SESSION_TTL = 86400 * 30
if OPENAI_API_KEY:
    try:
        llm = ChatOpenAI(
            model="qwen3.6-flash",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY,
            base_url=BASE_URL,
            streaming=True,
        )
    except Exception as e:
        print(f"LLM init error: {e}")


SYSTEM_PROMPT = "你是一个 AI 语言学习助手 LangMentor。你的任务是帮助用户学习语言。你会根据提供的上下文知识来回答用户的问题。如果上下文中有相关信息，请基于上下文回答；如果没有，请基于你的知识回答。回答要简洁、清晰、有帮助。"


@tool
def get_current_location() -> str:
    """Return the user's current location."""
    return "Beijing"


tools = [get_current_location]

if llm:
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)


class GenerateRequest(BaseModel):
    message: str
    context: Optional[List[dict]] = None
    session_id: Optional[str] = None


class GenerateResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


class SessionMessage(BaseModel):
    role: str
    content: str


class SessionData(BaseModel):
    session_id: str
    messages: List[SessionMessage]


def _get_session_from_redis(session_id: str) -> list:
    data = redis_client.get(f"session:{session_id}")
    if not data:
        return []
    try:
        msg_list = json.loads(data)
        return messages_from_dict(msg_list)
    except:
        return []


def _save_session_to_redis(session_id: str, messages: list):
    if not session_id:
        return
    msg_data = [message_to_dict(m) for m in messages[-20:]]
    redis_client.setex(f"session:{session_id}", SESSION_TTL, json.dumps(msg_data))


def _save_session(session_id: str, messages: list):
    _save_session_to_redis(session_id, messages)
    msg_list = [
        {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
        for m in messages
    ]
    persist_chat_session.delay(session_id, msg_list)


def _build_messages(request: GenerateRequest) -> list:
    context_text = ""
    if request.context:
        parts = [f"- {c.get('content', '')}" for c in request.context if c.get("content")]
        if parts:
            context_text = "\n\n相关上下文:\n" + "\n".join(parts)

    messages = _get_session_from_redis(request.session_id or "")

    user_content = request.message
    if context_text:
        user_content += context_text
    messages.append(HumanMessage(content=user_content))
    return messages


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm-service"}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    messages = _get_session_from_redis(session_id)
    return SessionData(
        session_id=session_id,
        messages=[
            SessionMessage(role="user" if isinstance(m, HumanMessage) else "assistant", content=m.content)
            for m in messages
        ]
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="LLM not initialized")
    try:
        messages = _build_messages(request)
        result = agent.invoke({"messages": messages})
        response_text = ""
        for msg in result.get("messages", []):
            if isinstance(msg, AIMessage) and msg.content:
                response_text = msg.content

        if request.session_id:
            msgs = _get_session_from_redis(request.session_id)
            msgs.append(HumanMessage(content=request.message))
            msgs.append(AIMessage(content=response_text))
            _save_session(request.session_id, msgs)
        return GenerateResponse(response=response_text, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/stream")
async def generate_stream(request: GenerateRequest):
    async def generate() -> Generator[str, None, None]:
        try:
            if not agent:
                yield f"data: {json.dumps({'error': 'LLM not initialized'})}\n\n"
                return

            messages = _build_messages(request)
            full_response = ""

            async for event in agent.astream_events(
                {"messages": messages}, version="v2"
            ):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        full_response += chunk.content
                        yield f"data: {json.dumps({'content': chunk.content})}\n\n"
                        await asyncio.sleep(0.03)

            if request.session_id:
                msgs = _get_session_from_redis(request.session_id)
                msgs.append(HumanMessage(content=request.message))
                msgs.append(AIMessage(content=full_response))
                _save_session(request.session_id, msgs)
            yield f"data: {json.dumps({'done': True, 'session_id': request.session_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
