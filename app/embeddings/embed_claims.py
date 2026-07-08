import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
import os

load_dotenv()

def claim_to_text(claim: dict) -> str:
    denial_part = f"Denial reason: {claim['denial_reason']}." if claim['denial_reason'] and str(claim['denial_reason']) != 'nan' else ""
    return f"""
Claim ID {claim['claim_id']} for patient {claim['patient_id']}.
Date of service: {claim['date_of_service']}.
Procedure: {claim['cpt_description']} (CPT {claim['cpt_code']}).
Payer: {claim['payer']}.
Diagnosis code: {claim['diagnosis_code']}.
Billed amount: ${claim['billed_amount']:.2f}.
Allowed amount: ${claim['allowed_amount']:.2f}.
Paid amount: ${claim['paid_amount']:.2f}.
Status: {claim['status']}. {denial_part}
Provider NPI: {claim['provider_npi']}.
""".strip()

def get_qdrant_client():
    os.makedirs("data/qdrant_storage", exist_ok=True)
    return QdrantClient(path="data/qdrant_storage")

def get_embedding_model():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

def run_embedding_pipeline():
    df = pd.read_csv("data/raw/claims.csv")
    print(f"Loaded {len(df)} claims for embedding")

    print("Loading embedding model...")
    model = get_embedding_model()

    texts = [claim_to_text(row) for _, row in df.iterrows()]
    print(f"Sample chunk:\n{texts[0]}\n")

    print("Embedding claims...")
    embeddings = list(model.embed(texts))
    import numpy as np
    embeddings = np.array(embeddings)
    print(f"Embeddings shape: {embeddings.shape}")

    client = get_qdrant_client()
    collection_name = os.getenv("QDRANT_COLLECTION", "healthclaim_embeddings")

    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=embeddings.shape[1], distance=Distance.COSINE)
    )

    points = []
    for i, (embedding, (_, row)) in enumerate(zip(embeddings, df.iterrows())):
        points.append(PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={
                "claim_id": row["claim_id"],
                "patient_id": row["patient_id"],
                "payer": row["payer"],
                "cpt_code": row["cpt_code"],
                "cpt_description": row["cpt_description"],
                "status": row["status"],
                "denial_reason": str(row["denial_reason"]) if str(row["denial_reason"]) != "nan" else None,
                "billed_amount": float(row["billed_amount"]),
                "paid_amount": float(row["paid_amount"]),
                "date_of_service": row["date_of_service"],
                "diagnosis_code": row["diagnosis_code"],
                "text": texts[i]
            }
        ))

    batch_size = 100
    for i in range(0, len(points), batch_size):
        client.upsert(collection_name=collection_name, points=points[i:i+batch_size])
        print(f"Uploaded {min(i+batch_size, len(points))}/{len(points)} points")

    print(f"\nDone! {client.count(collection_name).count} vectors stored")

if __name__ == "__main__":
    run_embedding_pipeline()
