from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.router import router_node
from app.agent.rag_node import rag_node
from app.agent.sql_node import sql_node
from app.agent.synthesizer import synthesizer_node
from app.guardrails.guardrails import run_input_guardrails, run_output_guardrails

def should_run_rag(state: AgentState) -> str:
    return "rag" if state["route"] in ["rag", "both"] else "sql"

def after_rag(state: AgentState) -> str:
    return "sql" if state["route"] == "both" else "synthesizer"

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("rag", rag_node)
    graph.add_node("sql", sql_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        should_run_rag,
        {"rag": "rag", "sql": "sql"}
    )
    graph.add_conditional_edges(
        "rag",
        after_rag,
        {"sql": "sql", "synthesizer": "synthesizer"}
    )
    graph.add_edge("sql", "synthesizer")
    graph.add_edge("synthesizer", END)
    return graph.compile()

agent = build_graph()

def run_agent(question: str) -> dict:
    # INPUT GUARDRAILS
    passed, message = run_input_guardrails(question)
    if not passed:
        return {
            "question": question,
            "route": "blocked",
            "final_answer": message,
            "sources": [],
            "rag_context": None,
            "sql_result": None,
            "error": message
        }

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

    # OUTPUT GUARDRAILS
    verified_answer, warnings = run_output_guardrails(
        result.get("final_answer", ""),
        result.get("sources") or []
    )
    result["final_answer"] = verified_answer
    if warnings:
        result["guardrail_warnings"] = warnings

    return result
