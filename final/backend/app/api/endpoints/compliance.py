"""
Compliance Citation Search API Endpoint + Dynamic RAG Document Uploader
"""

import os
import math
import re
from collections import Counter
from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.engine.schema import ComplianceCheckRequest, ComplianceCitation
from app.services.compliance_citation import ComplianceCitationService

router = APIRouter()
citation_service = ComplianceCitationService()

# In-memory RAG document store (uploaded standard documents)
_uploaded_documents: list = []


@router.post("/compliance-check", response_model=List[ComplianceCitation])
def compliance_check(request: ComplianceCheckRequest):
    """
    Execute statutory compliance retrieval against OISD / Factory Act standards.
    Evaluates real zone_id, permit_type, isolation_status, and gas_z_score dynamically.
    """
    results = citation_service.search_compliance_citations(
        zone_id=request.zone_id,
        permit_type=request.permit_type.value if request.permit_type else None,
        query_text=request.query_text,
        isolation_status=request.isolation_status,
        gas_z_score=request.gas_z_score
    )
    return results


@router.post("/compliance/upload-standard")
async def upload_compliance_standard(
    file: UploadFile = File(...),
    standard_name: str = Form(default="Uploaded Standard")
):
    """
    Upload a new statutory standard (PDF/TXT) to the RAG compliance engine.
    The document is chunked and vectorised using TF-IDF for dynamic compliance queries.
    Accepts plain text or UTF-8 encoded PDF text content.
    """
    content = await file.read()

    # Decode bytes to text (try UTF-8, fallback to latin-1)
    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception:
        text = content.decode("latin-1", errors="ignore")

    # Simple chunking: split into ~200 word chunks with 20-word overlap
    words = text.split()
    chunk_size = 200
    overlap = 20
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap

    doc_id = f"DOC-{len(_uploaded_documents) + 1:03d}"
    doc_record = {
        "doc_id": doc_id,
        "filename": file.filename,
        "standard_name": standard_name,
        "total_chunks": len(chunks),
        "chunks": chunks,
        "word_count": len(words)
    }
    _uploaded_documents.append(doc_record)

    return {
        "status": "DOCUMENT_INGESTED",
        "doc_id": doc_id,
        "filename": file.filename,
        "standard_name": standard_name,
        "total_chunks": len(chunks),
        "word_count": len(words),
        "message": f"'{file.filename}' vectorised and indexed. {len(chunks)} chunks added to RAG compliance engine."
    }


@router.get("/compliance/uploaded-standards")
def list_uploaded_standards():
    """
    List all documents uploaded to the RAG compliance engine.
    """
    summaries = [
        {
            "doc_id": d["doc_id"],
            "filename": d["filename"],
            "standard_name": d["standard_name"],
            "total_chunks": d["total_chunks"],
            "word_count": d["word_count"]
        }
        for d in _uploaded_documents
    ]
    return {"documents": summaries, "total_documents": len(summaries)}


@router.post("/compliance/rag-query")
async def rag_compliance_query(
    query: str = Form(...),
    top_k: int = Form(default=3)
):
    """
    Query the RAG compliance engine across all uploaded documents using TF-IDF cosine similarity.
    Returns top_k most relevant passages from uploaded standards.
    """
    if not _uploaded_documents:
        return {
            "results": [],
            "message": "No documents uploaded yet. Upload a PDF or TXT standard first via /compliance/upload-standard."
        }

    def tokenise(text):
        return re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())

    def cosine_similarity(query_tokens, chunk_text):
        chunk_tokens = tokenise(chunk_text)
        if not chunk_tokens:
            return 0.0
        chunk_counter = Counter(chunk_tokens)
        query_counter = Counter(query_tokens)
        dot = sum(query_counter[t] * chunk_counter.get(t, 0) for t in query_counter)
        mag_q = math.sqrt(sum(v**2 for v in query_counter.values()))
        mag_c = math.sqrt(sum(v**2 for v in chunk_counter.values()))
        if mag_q == 0 or mag_c == 0:
            return 0.0
        return dot / (mag_q * mag_c)

    query_tokens = tokenise(query)
    scored_chunks = []

    for doc in _uploaded_documents:
        for i, chunk in enumerate(doc["chunks"]):
            score = cosine_similarity(query_tokens, chunk)
            if score > 0:
                scored_chunks.append({
                    "doc_id": doc["doc_id"],
                    "standard_name": doc["standard_name"],
                    "filename": doc["filename"],
                    "chunk_index": i,
                    "passage": chunk[:600] + ("..." if len(chunk) > 600 else ""),
                    "relevance_score": round(score, 4)
                })

    scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
    top_results = scored_chunks[:top_k]

    return {
        "query": query,
        "top_k": top_k,
        "total_chunks_searched": sum(len(d["chunks"]) for d in _uploaded_documents),
        "results": top_results
    }
