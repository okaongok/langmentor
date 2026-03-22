from collections.abc import AsyncIterator

from langchain_core.prompts import ChatPromptTemplate
from .llm import get_llm

TRANSLATOR_SYSTEM_PROMPT = """你是一位温暖热心的专业翻译官，能自动识别中英文（文本或语音），并精准互译：用户说中文，你直接回英文；说英文，你直接回中文。保持语气自然，不加多余话语。若用户要求解释句子含义，请结合语境清晰说明；若用户说"别翻译了，聊聊天"，则切换为友好闲聊模式。始终以用户需求为准，简洁、准确、有温度。"""

EXPLAIN_SYSTEM_PROMPT = """你是一位专业的语言学习助手。用户会给你一个单词，请用中文解释：
1. 中文释义
2. 词性
3. 英文定义
4. 2-3个例句（附中文翻译）
5. 常见搭配或短语
格式清晰，简洁准确。"""

GRAMMAR_SYSTEM_PROMPT = """你是一位细心的语法老师。请检查用户提供的英文文本：
1. 找出语法错误
2. 给出修改后的正确版本
3. 用中文解释错误原因
简洁明了，重点突出。"""

EXERCISE_SYSTEM_PROMPT = """你是一位有经验的语言老师。根据用户提供的主题，生成5道英语练习题，包含：
1. 填空题
2. 选择题
3. 英译中/中译英
最后附上答案。题目难度适中，适合初中级学习者。"""

CHAT_SYSTEM_PROMPT = """你是一位温暖热心的语言学习伙伴。用户正在练习英语，你需要：
- 用简洁自然的英语交流
- 轻柔地纠正用户的错误
- 鼓励用户继续练习
- 如果用户要求，可以提供中文翻译
保持语气友好、有温度，让对话自然流畅。"""


def translate_tool(text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRANSLATOR_SYSTEM_PROMPT),
            ("user", text),
        ]
    )
    chain = prompt | llm
    response = chain.invoke({})
    return response.content


def explain_word_tool(word: str) -> str:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXPLAIN_SYSTEM_PROMPT),
            ("user", f"请解释这个单词：{word}"),
        ]
    )
    chain = prompt | llm
    response = chain.invoke({})
    return response.content


def check_grammar_tool(text: str) -> str:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", GRAMMAR_SYSTEM_PROMPT),
            ("user", f"请检查这段英文：{text}"),
        ]
    )
    chain = prompt | llm
    response = chain.invoke({})
    return response.content


def generate_exercise_tool(topic: str = "general") -> str:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXERCISE_SYSTEM_PROMPT),
            ("user", f"主题：{topic}"),
        ]
    )
    chain = prompt | llm
    response = chain.invoke({})
    return response.content


def chat_tool(message: str, history: list[dict] | None = None) -> str:
    llm = get_llm()
    messages = [("system", CHAT_SYSTEM_PROMPT)]

    if history:
        for msg in history:
            messages.append((msg["role"], msg["content"]))

    messages.append(("user", message))

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm
    response = chain.invoke({})
    return response.content


# Streaming versions


async def translate_stream(
    text: str, source_lang: str = "en", target_lang: str = "zh"
) -> AsyncIterator[str]:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRANSLATOR_SYSTEM_PROMPT),
            ("user", text),
        ]
    )
    chain = prompt | llm
    async for chunk in chain.astream({}):
        if chunk.content:
            yield chunk.content


async def explain_word_stream(word: str) -> AsyncIterator[str]:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXPLAIN_SYSTEM_PROMPT),
            ("user", f"请解释这个单词：{word}"),
        ]
    )
    chain = prompt | llm
    async for chunk in chain.astream({}):
        if chunk.content:
            yield chunk.content


async def check_grammar_stream(text: str) -> AsyncIterator[str]:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", GRAMMAR_SYSTEM_PROMPT),
            ("user", f"请检查这段英文：{text}"),
        ]
    )
    chain = prompt | llm
    async for chunk in chain.astream({}):
        if chunk.content:
            yield chunk.content


async def generate_exercise_stream(topic: str = "general") -> AsyncIterator[str]:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXERCISE_SYSTEM_PROMPT),
            ("user", f"主题：{topic}"),
        ]
    )
    chain = prompt | llm
    async for chunk in chain.astream({}):
        if chunk.content:
            yield chunk.content


async def chat_stream(
    message: str, history: list[dict] | None = None
) -> AsyncIterator[str]:
    llm = get_llm()
    messages = [("system", CHAT_SYSTEM_PROMPT)]

    if history:
        for msg in history:
            messages.append((msg["role"], msg["content"]))

    messages.append(("user", message))

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm
    async for chunk in chain.astream({}):
        if chunk.content:
            yield chunk.content
