from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import NamedVector
from app.agent.state import AgentState
from dotenv import load_dotenv
import os

load_dotenv()

model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
client = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)
COLLECTION = os.getenv("QDRANT_COLLECTION", "healthclaim_embeddings")

def rag_node(state: AgentState) -> AgentState:
    question = state["question"]
    
    # Embed the question
    query_vector = model.encode(question).tolist()
    
    # Search Qdrant using query_points (new API)
    results = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=5,
        with_payload=True
    ).points
    
    # Format retrieved chunks as context
    context_parts = []
    sources = []
    
    for i, result in enumerate(results):
        payload = result.payload
        context_parts.append(f"[Source {i+1}] {payload['text']}")
        sources.append({
            "claim_id": payload["claim_id"],
            "payer": payload["payer"],
            "status": payload["status"],
            "denial_reason": payload.get("denial_reason"),
            "score": round(result.score, 3)
        })
    
    rag_context = "\n\n".join(context_parts)
    print(f"[RAG Node] Retrieved {len(results)} relevant claims")
    
    return {**state, "rag_context": rag_context, "sources": sources}
