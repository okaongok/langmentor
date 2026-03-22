import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm() -> ChatOpenAI:
    """Get configured ChatOpenAI instance using Alibaba DashScope."""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
    base_url = os.getenv(
        "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    if not api_key or api_key == "your-api-key-here":
        raise ValueError("Please set DASHSCOPE_API_KEY in .env file")

    return ChatOpenAI(
        model=model,
        temperature=0.7,
        api_key=api_key,
        base_url=base_url,
    )
