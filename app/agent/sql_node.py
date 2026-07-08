from langchain_groq import ChatGroq
from app.agent.state import AgentState
from app.db import get_db_connection, get_table_name
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0
)

DB_SCHEMA = """
Table: {table_name}
Columns:
- claim_id (text): unique claim identifier e.g. CLM00001
- patient_id (text): patient identifier e.g. PAT0001
- date_of_service (text): date in YYYY-MM-DD format
- cpt_code (text): procedure code e.g. 99213
- cpt_description (text): procedure name
- payer (text): insurance company name (UnitedHealthcare, Aetna, Cigna, BlueCross, Humana)
- billed_amount (float): amount billed
- allowed_amount (float): amount allowed
- paid_amount (float): amount paid
- status (text): PAID or DENIED
- denial_reason (text): reason for denial if denied, null if paid
- provider_npi (text): provider identifier
- diagnosis_code (text): ICD-10 code

IMPORTANT: Always use the exact table name: {table_name}
"""

SQL_PROMPT = """You are a SQL expert for a healthcare claims database.
Given the schema and question, write a single valid SQL query.
Return ONLY the SQL query, no explanation, no markdown, no backticks.
Always use the exact table name shown in the schema.

Schema:
{schema}

Question: {question}
"""

def sql_node(state: AgentState) -> AgentState:
    question = state["question"]
    table_name = get_table_name()
    schema = DB_SCHEMA.format(table_name=table_name)

    response = llm.invoke(SQL_PROMPT.format(schema=schema, question=question))
    sql_query = response.content.strip()
    print(f"[SQL Node] Generated query:\n{sql_query}")

    try:
        conn, db_type = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()

        if not rows:
            sql_result = "No results found."
        else:
            lines = [" | ".join(col_names)]
            lines.append("-" * 60)
            for row in rows[:20]:
                lines.append(" | ".join(str(v) for v in row))
            sql_result = "\n".join(lines)

        print(f"[SQL Node] Query returned {len(rows)} rows")

    except Exception as e:
        sql_result = f"Query error: {str(e)}"
        print(f"[SQL Node] Error: {e}")

    return {**state, "sql_result": sql_result}
