import requests
import pandas as pd
import os

os.makedirs("data/raw", exist_ok=True)

# CMS Synthetic Patient Data - free and public
url = "https://raw.githubusercontent.com/synthetichealth/synthea/master/src/test/resources/generic/example_module.json"

# We'll generate synthetic claims directly
import json
import random
from datetime import datetime, timedelta

random.seed(42)

PAYERS = ["UnitedHealthcare", "Aetna", "Cigna", "BlueCross", "Humana"]
DENIAL_REASONS = [
    "Service not covered under plan",
    "Prior authorization required",
    "Duplicate claim submission",
    "Patient not eligible on date of service",
    "Medical necessity not established",
    "Out of network provider",
    "Claim filed after deadline",
    "Missing or invalid diagnosis code"
]
CPT_CODES = {
    "99213": "Office visit - established patient",
    "99214": "Office visit - complex",
    "93000": "Electrocardiogram",
    "71046": "Chest X-ray",
    "80053": "Comprehensive metabolic panel",
    "99283": "Emergency dept visit - moderate",
    "27447": "Total knee replacement",
    "43239": "Upper GI endoscopy with biopsy"
}

claims = []
for i in range(500):
    cpt = random.choice(list(CPT_CODES.keys()))
    payer = random.choice(PAYERS)
    denied = random.random() < 0.35
    date = datetime.now() - timedelta(days=random.randint(1, 365))
    billed = round(random.uniform(150, 8000), 2)
    
    claims.append({
        "claim_id": f"CLM{str(i+1).zfill(5)}",
        "patient_id": f"PAT{str(random.randint(1,100)).zfill(4)}",
        "date_of_service": date.strftime("%Y-%m-%d"),
        "cpt_code": cpt,
        "cpt_description": CPT_CODES[cpt],
        "payer": payer,
        "billed_amount": billed,
        "allowed_amount": round(billed * random.uniform(0.4, 0.9), 2) if not denied else 0,
        "paid_amount": round(billed * random.uniform(0.3, 0.8), 2) if not denied else 0,
        "status": "DENIED" if denied else "PAID",
        "denial_reason": random.choice(DENIAL_REASONS) if denied else None,
        "provider_npi": f"NPI{random.randint(1000000000, 9999999999)}",
        "diagnosis_code": random.choice(["Z00.00", "I10", "E11.9", "J06.9", "M54.5", "F32.9"])
    })

df = pd.DataFrame(claims)
df.to_csv("data/raw/claims.csv", index=False)
print(f"Generated {len(df)} claims")
print(f"Denied: {len(df[df['status']=='DENIED'])} ({len(df[df['status']=='DENIED'])/len(df)*100:.1f}%)")
print(f"Paid: {len(df[df['status']=='PAID'])}")
print(df.head())
