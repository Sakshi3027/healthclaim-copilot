from langchain_groq import ChatGroq
from app.agent.state import AgentState
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0
)

ROUTER_PROMPT = """You are a routing agent for a healthcare claims analysis system.
Given a user question, decide which data source to query:

- "rag": Question asks about specific claims, denial reasons, or needs examples
  Examples: "Why are claims being denied?", "Show me denied claims for UnitedHealthcare"
  
- "sql": Question asks for counts, aggregates, statistics, or comparisons
  Examples: "How many claims were denied?", "What is the denial rate by payer?"
  
- "both": Question needs both specific examples AND statistics
  Examples: "Which payer denies the most claims and why?", "Analyze denial patterns"

Respond with ONLY one word: rag, sql, or both.

Question: {question}
"""

def router_node(state: AgentState) -> AgentState:
    question = state["question"]
    response = llm.invoke(ROUTER_PROMPT.format(question=question))
    route = response.content.strip().lower()
    
    if route not in ["rag", "sql", "both"]:
        route = "both"
    
    print(f"[Router] Question: '{question}' → Route: {route}")
    return {**state, "route": route}
