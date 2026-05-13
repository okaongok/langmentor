from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down RAG Service...")


app = FastAPI(title="LangMentor RAG Service", version="0.1.0", lifespan=lifespan)

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

embeddings = None
if OPENAI_API_KEY:
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-v2",
            openai_api_key=OPENAI_API_KEY,
            base_url=BASE_URL,
            check_embedding_ctx_length=False
        )
    except Exception as e:
        print(f"Embedding init error: {e}")

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

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_text(doc.content)

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
            return {"documents": [], "total": 0}

        collection = vectorstore._collection
        count = collection.count()
        return {"documents": [], "total": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    try:
        if not vectorstore or not embeddings:
            return RetrieveResponse(results=[])

        results = vectorstore.similarity_search(request.query, k=request.top_k)

        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })

        return RetrieveResponse(results=formatted_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
