import dlt
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# Read the generated claims
df = pd.read_csv("data/raw/claims.csv")

# Convert to list of dicts for dlt
claims_data = df.to_dict(orient="records")

# Define dlt pipeline
pipeline = dlt.pipeline(
    pipeline_name="healthclaim_pipeline",
    destination=dlt.destinations.postgres(
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    ),
    dataset_name="claims"
)

# Define resource
@dlt.resource(name="insurance_claims", write_disposition="replace")
def insurance_claims():
    for claim in claims_data:
        yield claim

# Run pipeline
load_info = pipeline.run(insurance_claims())
print("Pipeline completed!")
print(load_info)
