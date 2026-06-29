from langchain_groq import ChatGroq
from app.agent.state import AgentState
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.2
)

SYNTH_PROMPT = """You are a healthcare claims analysis expert.
Answer the user's question using the provided context.
Always cite specific claim IDs when referencing examples.
Be concise, specific, and actionable.

User Question: {question}

{rag_section}

{sql_section}

Provide a clear, structured answer with:
1. Direct answer to the question
2. Supporting evidence from the data (cite claim IDs)
3. Key insight or recommendation

Answer:"""

def synthesizer_node(state: AgentState) -> AgentState:
    question = state["question"]
    
    rag_section = ""
    if state.get("rag_context"):
        rag_section = f"Relevant Claims (from semantic search):\n{state['rag_context']}"
    
    sql_section = ""
    if state.get("sql_result"):
        sql_section = f"Statistical Data (from database query):\n{state['sql_result']}"
    
    prompt = SYNTH_PROMPT.format(
        question=question,
        rag_section=rag_section,
        sql_section=sql_section
    )
    
    response = llm.invoke(prompt)
    final_answer = response.content.strip()
    
    print(f"[Synthesizer] Generated answer ({len(final_answer)} chars)")
    return {**state, "final_answer": final_answer}
