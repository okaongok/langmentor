from celery-worker.config import celery_app
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, SystemMessage
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


@celery_app.task(bind=True)
def process_document(self, title: str, content: str, source: str = ""):
    """异步处理文档：分割、嵌入、存储到向量数据库"""
    try:
        self.update_state(state="PROGRESS", meta={"step": "splitting"})

        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_text(content)

        self.update_state(state="PROGRESS", meta={"step": "embedding", "chunks": len(chunks)})

        # 生成嵌入并存储
        if OPENAI_API_KEY:
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            metadatas = [
                {
                    "title": title,
                    "source": source,
                    "chunk_index": i
                }
                for i in range(len(chunks))
            ]

            vectorstore = Chroma(
                collection_name="langmentor_docs",
                embedding_function=embeddings,
                persist_directory="./chroma_db"
            )
            vectorstore.add_texts(chunks, metadatas=metadatas)
            vectorstore.persist()

        return {
            "status": "success",
            "title": title,
            "chunks_processed": len(chunks)
        }
    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery_app.task(bind=True)
def generate_response(self, message: str, context: list = None, session_id: str = None):
    """异步生成 LLM 响应"""
    try:
        self.update_state(state="PROGRESS", meta={"step": "generating"})

        if not OPENAI_API_KEY:
            return {"status": "error", "message": "OpenAI API key not configured"}

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )

        system_prompt = """你是一个 AI 语言学习助手 LangMentor。帮助用户学习语言。"""

        messages = [SystemMessage(content=system_prompt)]

        # 添加上下文
        if context:
            context_text = "\n\n相关上下文:\n" + "\n".join(
                [f"- {ctx.get('content', '')}" for ctx in context]
            )
            message += context_text

        messages.append(HumanMessage(content=message))

        response = llm.invoke(messages)

        return {
            "status": "success",
            "response": response.content,
            "session_id": session_id
        }
    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery_app.task
def health_check():
    """健康检查任务"""
    return {"status": "healthy", "service": "celery-worker"}
