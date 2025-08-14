import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rag_chain import query_rag
from ingest import ingest_documents
import asyncio
import json

app = FastAPI(
    title="RAG Programming Assistant API",
    description="API untuk berinteraksi dengan RAG assistant dan mengelola dokumen.",
    version="1.0.0",
)

class QueryRequest(BaseModel):
    question: str
    category: str | None = None
    temperature: float = 0.8
    max_tokens: int = 8192
    gpu_layers: int = 30

@app.post("/query")
async def handle_query(request: QueryRequest):
    """Menerima pertanyaan dan mengembalikan jawaban secara streaming."""
    async def stream_generator():
        # query_rag is a generator, we need to iterate over it
        for chunk_data in query_rag(
            question=request.question,
            category=request.category,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            gpu_layers=request.gpu_layers
        ):
            # Serialize the dictionary to a JSON string followed by a newline
            yield json.dumps(chunk_data) + "\n"
            await asyncio.sleep(0.01) # A small delay for smooth streaming

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

@app.post("/ingest", status_code=202)
def handle_ingest():
    """Memicu proses ingesti dokumen di latar belakang."""
    # Dalam produksi, ini sebaiknya dijalankan di background thread
    ingest_documents()
    return {"message": "Proses ingesti dokumen telah dimulai."}