from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Generator
import os
import json
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

app = FastAPI(title="LangMentor LLM Service", version="0.1.0")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# 初始化 LLM
llm = None
if OPENAI_API_KEY:
    try:
        llm = ChatOpenAI(
            model="qwen3.6-flash",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY,
            base_url=BASE_URL,
            streaming=True
        )
    except Exception as e:
        print(f"LLM init error: {e}")


class GenerateRequest(BaseModel):
    message: str
    context: Optional[List[dict]] = None
    session_id: Optional[str] = None


class GenerateResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


@app.post("/generate/stream")
async def generate_stream(request: GenerateRequest):
    """流式生成回复"""
    async def generate() -> Generator[str, None, None]:
        try:
            if not llm:
                yield "data: " + json.dumps({"error": "LLM not initialized"}) + "\n\n"
                return

            context_text = ""
            if request.context:
                context_text = "\n\n相关上下文:\n" + "\n".join(
                    [f"- {ctx.get('content', '')}" for ctx in request.context]
                )

            system_prompt = """你是一个 AI 语言学习助手 LangMentor。你的任务是帮助用户学习语言。
            你会根据提供的上下文知识来回答用户的问题。如果上下文中有相关信息，请基于上下文回答；
            如果没有，请基于你的知识回答。回答要简洁、清晰、有帮助。"""

            messages = [SystemMessage(content=system_prompt)]

            if request.session_id and request.session_id in sessions:
                messages.extend(sessions[request.session_id])

            user_content = request.message
            if context_text:
                user_content += context_text

            messages.append(HumanMessage(content=user_content))

            full_response = ""
            async for chunk in llm.astream(messages):
                content = chunk.content
                if content:
                    full_response += content
                    yield "data: " + json.dumps({"content": content}) + "\n\n"
                    await asyncio.sleep(0.03)

            if request.session_id:
                if request.session_id not in sessions:
                    sessions[request.session_id] = []
                sessions[request.session_id].append(HumanMessage(content=request.message))
                sessions[request.session_id].append(AIMessage(content=full_response))
                if len(sessions[request.session_id]) > 20:
                    sessions[request.session_id] = sessions[request.session_id][-20:]

            yield "data: " + json.dumps({"done": True, "session_id": request.session_id}) + "\n\n"

        except Exception as e:
            yield "data: " + json.dumps({"error": str(e)}) + "\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# 简单的内存会话存储
sessions = {}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm-service"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    try:
        if not llm:
            raise HTTPException(status_code=503, detail="LLM not initialized")

        # 构建上下文
        context_text = ""
        if request.context:
            context_text = "\n\n相关上下文:\n" + "\n".join(
                [f"- {ctx.get('content', '')}" for ctx in request.context]
            )

        # 构建系统提示
        system_prompt = """你是一个 AI 语言学习助手 LangMentor。你的任务是帮助用户学习语言。
你会根据提供的上下文知识来回答用户的问题。如果上下文中有相关信息，请基于上下文回答；
如果没有，请基于你的知识回答。回答要简洁、清晰、有帮助。"""

        # 构建消息
        messages = [SystemMessage(content=system_prompt)]

        # 添加历史消息（如果有会话）
        if request.session_id and request.session_id in sessions:
            messages.extend(sessions[request.session_id])

        # 添加用户消息
        user_content = request.message
        if context_text:
            user_content += context_text

        messages.append(HumanMessage(content=user_content))

        # 调用 LLM
        response = llm.invoke(messages)
        response_text = response.content

        # 保存会话
        if request.session_id:
            if request.session_id not in sessions:
                sessions[request.session_id] = []
            sessions[request.session_id].append(HumanMessage(content=request.message))
            sessions[request.session_id].append(AIMessage(content=response_text))
            # 限制历史长度
            if len(sessions[request.session_id]) > 20:
                sessions[request.session_id] = sessions[request.session_id][-20:]

        return GenerateResponse(
            response=response_text,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(message: str, session_id: Optional[str] = None):
    """简单的直接聊天接口"""
    try:
        if not llm:
            raise HTTPException(status_code=503, detail="LLM not initialized")

        messages = [HumanMessage(content=message)]
        response = llm.invoke(messages)

        return {"response": response.content, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
