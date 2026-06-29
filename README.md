# 🏥 HealthClaim Copilot

> Enterprise RAG agent for healthcare insurance claim analysis — built with LangGraph, Qdrant, Groq, Guardrails, and RAGAS evals.

**Live Demo:** [Coming soon — Render + Vercel]  
**Stack:** Python · FastAPI · LangGraph · Qdrant · PostgreSQL · Next.js · Groq · RAGAS

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
User Question

│

▼

┌─────────────┐

│   Guardrails │  ← PII detection, scope check, injection blocking

└─────┬───────┘

│

▼

┌─────────────┐

│   Router    │  ← LLM decides: RAG / SQL / Both

└──┬──────┬───┘

│      │

▼      ▼

┌──────┐ ┌──────┐

│ RAG  │ │ SQL  │  ← Qdrant vector search + PostgreSQL

│ Node │ │ Node │

└──┬───┘ └──┬───┘

└────┬───┘

▼

┌──────────────┐

│ Synthesizer  │  ← Combines context, cites claim IDs

└──────┬───────┘

│

▼

┌──────────────┐

│ Output Guard │  ← Hallucination check on cited claim IDs

└──────────────┘

## Key Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **RAG** | Claims chunked → embedded → stored in Qdrant → retrieved by semantic similarity |
| **Embeddings** | `all-MiniLM-L6-v2` (384-dim) via sentence-transformers, runs locally |
| **Vector Search** | Qdrant cosine similarity search, top-5 retrieval per query |
| **Agent Orchestration** | 4-node LangGraph graph: Router → RAG/SQL → Synthesizer |
| **Guardrails** | Input: PII/SSN detection, scope filtering, injection blocking. Output: hallucination verification |
| **Evals** | RAGAS-style golden dataset (10 questions), measuring answer relevance, faithfulness, route accuracy |

## Eval Results

| Metric | Score |
|--------|-------|
| Answer Relevance | 0.779 / 1.000 |
| Faithfulness | 0.494 / 1.000 |
| Route Accuracy | 0.900 / 1.000 (9/10) |
| **Overall** | **0.724 / 1.000** |

## Tech Stack

**Backend:** Python 3.12 · FastAPI · LangGraph · LangChain · Groq (llama-3.1-8b-instant)  
**Data:** dlt · PostgreSQL · Qdrant · sentence-transformers  
**Guardrails:** Custom PII detection · Pydantic validators · Hallucination verification  
**Evals:** RAGAS-style golden dataset · LangSmith tracing  
**Frontend:** Next.js 15 · TypeScript · Tailwind CSS  
**Infra:** Docker Compose · GitHub Actions (coming)

## Project Structure
healthclaim-copilot/

├── app/

│   ├── agent/          # LangGraph nodes (router, rag, sql, synthesizer)

│   ├── api/            # FastAPI endpoints

│   ├── embeddings/     # Embedding pipeline

│   ├── guardrails/     # Input/output guardrails

│   └── evals/          # Golden dataset + RAGAS scoring

├── data/

│   ├── raw/            # Generated synthetic CMS claims

│   └── processed/      # Eval results

├── docker/             # Docker Compose (PostgreSQL + Qdrant)

├── frontend/           # Next.js chat UI

└── requirements.txt

## Running Locally

```bash
# 1. Clone and setup
git clone https://github.com/Sakshi3027/healthclaim-copilot.git
cd healthclaim-copilot
conda create -n healthclaim python=3.12 -y
conda activate healthclaim
pip install -r requirements.txt

# 2. Start databases
cd docker && docker-compose up -d && cd ..

# 3. Add your keys to .env
cp .env.example .env
# Add GROQ_API_KEY and LANGCHAIN_API_KEY

# 4. Run data pipeline
python data/download_data.py
python data/load_to_postgres.py
python app/embeddings/embed_claims.py

# 5. Start backend
uvicorn app.api.main:app --reload --port 8000

# 6. Start frontend
cd frontend && npm install && npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask a natural language question |
| `/stats` | GET | Claims dataset statistics |
| `/evals` | GET | Latest eval results |
| `/health` | GET | Health check |

## Data

Uses synthetic CMS-style healthcare claims data (500 claims, 5 payers, 8 CPT codes). No real patient data — safe for public demo.

---

Built by [Sakshi Chavan](https://github.com/Sakshi3027) · MS Data Science, UMass Dartmouth
