import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is not None:
        return _llm

    api_key = os.getenv("DASHSCOPE_API_KEY")
    model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
    base_url = os.getenv(
        "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    if not api_key or api_key == "your-api-key-here":
        raise ValueError("Please set DASHSCOPE_API_KEY in .env file")

    _llm = ChatOpenAI(
        model=model,
        temperature=0.7,
        api_key=api_key,
        base_url=base_url,
        streaming=True,
        max_retries=2,
    )
    return _llm
