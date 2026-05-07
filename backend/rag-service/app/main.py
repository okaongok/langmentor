from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = FastAPI(title="LangMentor RAG Service", version="0.1.0")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 初始化 embedding 和 vector store
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
vectorstore = None

if embeddings:
    try:
        vectorstore = Chroma(
            collection_name="langmentor_docs",
            embedding_function=embeddings,
            persist_directory="./chroma_db"
        )
    except Exception as e:
        print(f"Chroma init error: {e}")


class DocumentRequest(BaseModel):
    title: str
    content: str
    source: str = ""
    metadata: Optional[dict] = None


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 3


class RetrieveResponse(BaseModel):
    results: List[dict]


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-service"}


@app.post("/documents")
async def create_document(doc: DocumentRequest):
    try:
        if not vectorstore or not embeddings:
            raise HTTPException(status_code=503, detail="Vector store not initialized")

        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_text(doc.content)

        # 添加到向量数据库
        metadatas = [
            {
                "title": doc.title,
                "source": doc.source,
                "chunk_index": i,
                **(doc.metadata or {})
            }
            for i in range(len(chunks))
        ]

        vectorstore.add_texts(chunks, metadatas=metadatas)
        vectorstore.persist()

        return {
            "status": "success",
            "message": f"Added {len(chunks)} chunks",
            "title": doc.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents():
    try:
        if not vectorstore:
            return {"documents": []}

        # 获取集合信息
        collection = vectorstore._collection
        count = collection.count()
        return {"documents": [], "total_chunks": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    try:
        if not vectorstore or not embeddings:
            return RetrieveResponse(results=[])

        results = vectorstore.similarity_search(
            request.query,
            k=request.top_k
        )

        formatted_results = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": 1.0  # Chroma 默认不返回 score
            }
            for doc in results
        ]

        return RetrieveResponse(results=formatted_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
