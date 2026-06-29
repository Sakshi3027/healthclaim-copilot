from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    question: str
    route: str                    # "rag", "sql", "both"
    rag_context: Optional[str]    # retrieved claim chunks
    sql_result: Optional[str]     # structured query result
    sources: Optional[List[dict]] # claim IDs cited
    final_answer: Optional[str]   # synthesized response
    error: Optional[str]
