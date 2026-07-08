# 🏥 HealthClaim Copilot

> Enterprise RAG agent for healthcare insurance claim analysis — built with LangGraph, Qdrant, Groq, Guardrails, and RAGAS evals.

**Live Demo:** https://healthclaim-copilot.vercel.app  
**Backend API:** https://healthclaim-copilot-api.onrender.com  
**Stack:** Python · FastAPI · LangGraph · Qdrant · SQLite · Next.js · Groq · RAGAS

---

## What It Does

HealthClaim Copilot is a production-grade AI agent that answers natural language questions about insurance claims data. It combines semantic search over claim documents with structured SQL queries — automatically routing each question to the right data source.

Ask it things like:
- *"Why are UnitedHealthcare claims being denied?"*
- *"What is the denial rate for Cigna?"*
- *"Show me denied claims for total knee replacement"*
- *"Which payer has the highest denial rate and what are the reasons?"*

---

## Architecture

The agent uses a 4-node LangGraph graph:

**User Question → Guardrails → Router → RAG Node / SQL Node → Synthesizer → Verified Answer**

| Node | Role |
|------|------|
| **Guardrails** | Blocks PII (SSN, DOB), out-of-scope questions, and injection attempts before hitting the LLM |
| **Router** | LLM decides whether the question needs semantic search (RAG), structured query (SQL), or both |
| **RAG Node** | Embeds the question, searches Qdrant for the 5 most relevant claims by cosine similarity |
| **SQL Node** | LLM generates a SQL query, executes it against the claims database, returns structured results |
| **Synthesizer** | Combines RAG context + SQL results into a cited, structured answer |
| **Output Guard** | Verifies every claim ID cited in the answer exists in retrieved sources |

---

## Key Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **RAG** | Claims chunked → embedded → stored in Qdrant → retrieved by semantic similarity |
| **Embeddings** | `BAAI/bge-small-en-v1.5` via fastembed (ONNX runtime, no PyTorch dependency) |
| **Vector Search** | Qdrant cosine similarity search, top-5 retrieval per query |
| **Agent Orchestration** | 4-node LangGraph graph with conditional routing |
| **Guardrails** | Input: PII/SSN detection, scope filtering, injection blocking. Output: hallucination verification |
| **Evals** | RAGAS-style golden dataset (10 questions), measuring answer relevance, faithfulness, route accuracy |

---

## Eval Results

| Metric | Score |
|--------|-------|
| Answer Relevance | 0.779 / 1.000 |
| Faithfulness | 0.494 / 1.000 |
| Route Accuracy | 0.900 / 1.000 (9/10) |
| **Overall** | **0.724 / 1.000** |

---

## Tech Stack

**Backend:** Python 3.12 · FastAPI · LangGraph · LangChain · Groq (llama-3.1-8b-instant)  
**Data:** dlt · SQLite · Qdrant · fastembed (BAAI/bge-small-en-v1.5)  
**Guardrails:** Custom PII detection · Pydantic validators · Hallucination verification  
**Evals:** RAGAS-style golden dataset · LangSmith tracing  
**Frontend:** Next.js 15 · TypeScript · Tailwind CSS  
**Deployment:** Render (backend) · Vercel (frontend)

---
## Project Structure

```
 healthclaim-copilot/
├── app/
│ ├── agent/ # LangGraph nodes (router, rag, sql, synthesizer)
│ ├── api/ # FastAPI endpoints (/ask, /stats, /health, /evals)
│ ├── embeddings/ # Embedding pipeline (fastembed + Qdrant)
│ ├── guardrails/ # Input/output guardrails
│ └── evals/ # Golden dataset + RAGAS-style scoring
├── data/
│ ├── raw/ # Synthetic CMS-style claims (500 records)
│ ├── claims.db # SQLite database
│ ├── qdrant_storage/ # Local vector store
│ └── processed/ # Eval results
├── docker/ # Docker Compose (local PostgreSQL + Qdrant)
├── frontend/ # Next.js chat UI
└── requirements.txt
```

## Running Locally

```bash
# 1. Clone and setup
git clone https://github.com/Sakshi3027/healthclaim-copilot.git
cd healthclaim-copilot
conda create -n healthclaim python=3.12 -y
conda activate healthclaim
pip install -r requirements-deploy.txt

# 2. Add your keys to .env
cp .env.example .env
# Add GROQ_API_KEY and LANGCHAIN_API_KEY

# 3. Run data pipeline
python data/download_data.py
python app/embeddings/embed_claims.py

# 4. Start backend
uvicorn app.api.main:app --reload --port 8000

# 5. Start frontend
cd frontend && npm install && npm run dev
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask a natural language question |
| `/stats` | GET | Claims dataset statistics |
| `/evals` | GET | Latest eval results |
| `/health` | GET | Health check |

---

## Data

Uses synthetic CMS-style healthcare claims data (500 claims, 5 payers, 8 CPT codes). No real patient data — safe for public demo.

---

Built by [Sakshi Chavan](https://github.com/Sakshi3027) · MS Data Science, UMass Dartmouth
