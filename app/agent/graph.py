from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.router import router_node
from app.agent.rag_node import rag_node
from app.agent.sql_node import sql_node
from app.agent.synthesizer import synthesizer_node

def should_run_rag(state: AgentState) -> str:
    return "rag" if state["route"] in ["rag", "both"] else "sql"

def after_rag(state: AgentState) -> str:
    return "sql" if state["route"] == "both" else "synthesizer"

def build_graph():
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("rag", rag_node)
    graph.add_node("sql", sql_node)
    graph.add_node("synthesizer", synthesizer_node)
    
    # Entry point
    graph.set_entry_point("router")
    
    # Router decides path
    graph.add_conditional_edges(
        "router",
        should_run_rag,
        {"rag": "rag", "sql": "sql"}
    )
    
    # After RAG - go to SQL if "both", else synthesize
    graph.add_conditional_edges(
        "rag",
        after_rag,
        {"sql": "sql", "synthesizer": "synthesizer"}
    )
    
    # SQL always goes to synthesizer
    graph.add_edge("sql", "synthesizer")
    
    # Synthesizer ends
    graph.add_edge("synthesizer", END)
    
    return graph.compile()

# Singleton
agent = build_graph()

def run_agent(question: str) -> dict:
    initial_state = AgentState(
        question=question,
        route="",
        rag_context=None,
        sql_result=None,
        sources=None,
        final_answer=None,
        error=None
    )
    result = agent.invoke(initial_state)
    return result
