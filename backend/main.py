from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.tools import (
    translate_stream,
    explain_word_stream,
    check_grammar_stream,
    generate_exercise_stream,
    chat_stream,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslationRequest(BaseModel):
    word: str
    source_lang: str = "en"
    target_lang: str = "zh"


class ExplainRequest(BaseModel):
    word: str


class GrammarRequest(BaseModel):
    text: str


class ExerciseRequest(BaseModel):
    topic: str = "general"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] | None = None


@app.post("/api/translate")
async def translate(request: TranslationRequest):
    async def generate():
        async for chunk in translate_stream(
            request.word, request.source_lang, request.target_lang
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/explain")
async def explain_word(request: ExplainRequest):
    async def generate():
        async for chunk in explain_word_stream(request.word):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/grammar")
async def check_grammar(request: GrammarRequest):
    async def generate():
        async for chunk in check_grammar_stream(request.text):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/exercise")
async def generate_exercise(request: ExerciseRequest):
    async def generate():
        async for chunk in generate_exercise_stream(request.topic):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    history_dicts = None
    if request.history:
        history_dicts = [msg.model_dump() for msg in request.history]

    async def generate():
        async for chunk in chat_stream(request.message, history_dicts):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
