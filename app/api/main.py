from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time
import os
import json
from dotenv import load_dotenv

load_dotenv()

from app.agent.graph import run_agent

app = FastAPI(
    title="HealthClaim Copilot API",
    description="Enterprise RAG agent for healthcare insurance claim analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class Source(BaseModel):
    claim_id: str
    payer: str
    status: str
    denial_reason: Optional[str]
    score: Optional[float]

class QuestionResponse(BaseModel):
    question: str
    answer: str
    route: str
    sources: Optional[List[Source]]
    latency_ms: float
    guardrail_warnings: Optional[List[str]]

@app.get("/")
def root():
    return {
        "name": "HealthClaim Copilot",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    start = time.time()
    result = run_agent(request.question)
    latency_ms = round((time.time() - start) * 1000, 2)

    sources = None
    if result.get("sources"):
        sources = [Source(**s) for s in result["sources"]]

    return QuestionResponse(
        question=request.question,
        answer=result.get("final_answer", ""),
        route=result.get("route", "unknown"),
        sources=sources,
        latency_ms=latency_ms,
        guardrail_warnings=result.get("guardrail_warnings")
    )

@app.get("/stats")
def stats():
    """Return high-level stats about the claims dataset."""
    import psycopg2
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB")
        )
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM claims.insurance_claims")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM claims.insurance_claims WHERE status='DENIED'")
        denied = cur.fetchone()[0]

        cur.execute("SELECT payer, COUNT(*) as cnt FROM claims.insurance_claims WHERE status='DENIED' GROUP BY payer ORDER BY cnt DESC")
        by_payer = {row[0]: row[1] for row in cur.fetchall()}

        cur.execute("SELECT denial_reason, COUNT(*) as cnt FROM claims.insurance_claims WHERE status='DENIED' AND denial_reason IS NOT NULL GROUP BY denial_reason ORDER BY cnt DESC LIMIT 5")
        top_reasons = {row[0]: row[1] for row in cur.fetchall()}

        cur.close()
        conn.close()

        return {
            "total_claims": total,
            "denied_claims": denied,
            "paid_claims": total - denied,
            "denial_rate": round(denied / total * 100, 1),
            "denials_by_payer": by_payer,
            "top_denial_reasons": top_reasons
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evals")
def evals():
    """Return latest eval results."""
    try:
        with open("data/processed/eval_results.json") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Eval results not found. Run app/evals/run_evals.py first.")
