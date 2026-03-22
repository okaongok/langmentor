from collections.abc import AsyncIterator

from langchain_core.messages import HumanMessage, SystemMessage
from .llm import get_llm

TRANSLATOR_SYSTEM_PROMPT = (
    "你是一位温暖热心的专业翻译官，能自动识别中英文，精准互译："
    "用户说中文，你直接回英文；说英文，你直接回中文。"
    "保持语气自然，简洁准确，不加多余话语。"
)

EXPLAIN_SYSTEM_PROMPT = (
    "你是一位专业的语言学习助手。用户给你一个单词，请用中文简洁解释："
    "中文释义、词性、英文定义、2-3个例句（附翻译）、常见搭配。"
)

GRAMMAR_SYSTEM_PROMPT = (
    "你是一位细心的语法老师。检查用户提供的英文文本："
    "找出语法错误，给出修改后的正确版本，用中文解释错误原因。简洁明了。"
)

EXERCISE_SYSTEM_PROMPT = (
    "你是一位有经验的语言老师。根据主题生成5道英语练习题，"
    "包含填空、选择、翻译题，最后附答案。"
)

CHAT_SYSTEM_PROMPT = (
    "你是一位温暖热心的语言学习伙伴。用简洁自然的英语交流，"
    "轻柔地纠正错误，鼓励用户练习。如果用户要求，提供中文翻译。"
)


async def translate_stream(
    text: str, source_lang: str = "en", target_lang: str = "zh"
) -> AsyncIterator[str]:
    llm = get_llm()
    async for chunk in llm.astream(
        [
            SystemMessage(content=TRANSLATOR_SYSTEM_PROMPT),
            HumanMessage(content=text),
        ]
    ):
        if chunk.content:
            yield chunk.content


async def explain_word_stream(word: str) -> AsyncIterator[str]:
    llm = get_llm()
    async for chunk in llm.astream(
        [
            SystemMessage(content=EXPLAIN_SYSTEM_PROMPT),
            HumanMessage(content=f"请解释这个单词：{word}"),
        ]
    ):
        if chunk.content:
            yield chunk.content


async def check_grammar_stream(text: str) -> AsyncIterator[str]:
    llm = get_llm()
    async for chunk in llm.astream(
        [
            SystemMessage(content=GRAMMAR_SYSTEM_PROMPT),
            HumanMessage(content=f"请检查这段英文：{text}"),
        ]
    ):
        if chunk.content:
            yield chunk.content


async def generate_exercise_stream(topic: str = "general") -> AsyncIterator[str]:
    llm = get_llm()
    async for chunk in llm.astream(
        [
            SystemMessage(content=EXERCISE_SYSTEM_PROMPT),
            HumanMessage(content=f"主题：{topic}"),
        ]
    ):
        if chunk.content:
            yield chunk.content


async def chat_stream(
    message: str, history: list[dict] | None = None
) -> AsyncIterator[str]:
    llm = get_llm()
    messages = [SystemMessage(content=CHAT_SYSTEM_PROMPT)]

    if history:
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(SystemMessage(content=msg["content"]))

    messages.append(HumanMessage(content=message))

    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content
