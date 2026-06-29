from app.agent.graph import run_agent

questions = [
    "How many claims were denied by each payer?",
    "Why are UnitedHealthcare claims being denied?",
    "Which payer has the highest denial rate and what are the most common reasons?"
]

for q in questions:
    print("\n" + "="*60)
    print(f"QUESTION: {q}")
    print("="*60)
    result = run_agent(q)
    print(f"\nROUTE: {result['route']}")
    print(f"\nANSWER:\n{result['final_answer']}")
    if result.get('sources'):
        print(f"\nSOURCES: {[s['claim_id'] for s in result['sources']]}")
