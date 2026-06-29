# Golden test set - questions with known correct answers from our data
# Used to evaluate RAG pipeline quality

GOLDEN_DATASET = [
    {
        "question": "How many claims were denied by UnitedHealthcare?",
        "ground_truth": "UnitedHealthcare denied 37 claims in the dataset.",
        "expected_route": "sql"
    },
    {
        "question": "What are the most common reasons for claim denials?",
        "ground_truth": "The most common denial reasons include: service not covered under plan, prior authorization required, out of network provider, medical necessity not established, and patient not eligible on date of service.",
        "expected_route": "both"
    },
    {
        "question": "Which payer has the lowest denial rate?",
        "ground_truth": "Humana has the lowest number of denied claims with 32 denials.",
        "expected_route": "sql"
    },
    {
        "question": "Show me denied claims for total knee replacement procedure",
        "ground_truth": "Several claims for CPT code 27447 (Total knee replacement) were denied, with reasons including service not covered under plan and prior authorization required.",
        "expected_route": "rag"
    },
    {
        "question": "What is the total billed amount for denied claims?",
        "ground_truth": "The total billed amount for all denied claims across all payers exceeds $100,000.",
        "expected_route": "sql"
    },
    {
        "question": "Why are claims being denied for out of network providers?",
        "ground_truth": "Claims are denied when the provider is not in the payer network. The denial reason is explicitly listed as out of network provider.",
        "expected_route": "rag"
    },
    {
        "question": "How many claims were denied due to prior authorization required?",
        "ground_truth": "Multiple claims were denied due to prior authorization being required but not obtained before service.",
        "expected_route": "sql"
    },
    {
        "question": "What is the average paid amount for Aetna claims?",
        "ground_truth": "The average paid amount for Aetna claims that were paid (not denied) is a non-zero dollar amount.",
        "expected_route": "sql"
    },
    {
        "question": "Show denied emergency department visits",
        "ground_truth": "Some emergency department visits (CPT 99283) were denied, with reasons including medical necessity not established and patient not eligible on date of service.",
        "expected_route": "rag"
    },
    {
        "question": "Which diagnosis code has the most denied claims?",
        "ground_truth": "The diagnosis codes with denied claims include F32.9, E11.9, M54.5, I10, Z00.00, and J06.9.",
        "expected_route": "sql"
    }
]
