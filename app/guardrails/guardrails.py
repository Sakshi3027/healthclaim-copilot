import re
from typing import Tuple

# ─────────────────────────────────────────
# 1. INPUT GUARDRAIL — PII Detection
# ─────────────────────────────────────────

PII_PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "DOB": r"\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\b",
    "Phone": r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",
    "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "CreditCard": r"\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b",
}

# Only block phrases that are clearly NOT claims analysis
OUT_OF_SCOPE_PHRASES = [
    "should i take",
    "medical advice",
    "what medication",
    "prescribe me",
    "my symptoms",
    "treat my",
    "invest in",
    "stock price",
    "legal advice",
    "sue my",
    "file a lawsuit",
]

def check_input(question: str) -> Tuple[bool, str]:
    # Check for PII
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, question, re.IGNORECASE):
            return False, f"❌ Input blocked: Detected {pii_type} in your question. Please remove personal identifiable information before submitting."

    # Check for out-of-scope phrases
    question_lower = question.lower()
    for phrase in OUT_OF_SCOPE_PHRASES:
        if phrase in question_lower:
            return False, f"❌ Out of scope: This system analyzes insurance claims data only. Questions about medical advice, legal matters, or investments are not supported."

    if len(question.strip()) < 5:
        return False, "❌ Question too short. Please provide a specific question about claims data."

    return True, "OK"


# ─────────────────────────────────────────
# 2. OUTPUT GUARDRAIL — Hallucination Check
# ─────────────────────────────────────────

def check_output(answer: str, sources: list) -> Tuple[str, list]:
    warnings = []
    if not sources:
        return answer, warnings

    cited_ids = set(re.findall(r"CLM\d{5}", answer))
    valid_ids = set(s["claim_id"] for s in sources)
    hallucinated = cited_ids - valid_ids

    if hallucinated:
        warning_msg = f"⚠️ Verification warning: The following claim IDs were mentioned but not found in retrieved sources: {', '.join(sorted(hallucinated))}. Please verify these independently."
        warnings.append(warning_msg)
        answer = answer + f"\n\n{warning_msg}"

    return answer, warnings


# ─────────────────────────────────────────
# 3. REFUSAL GUARDRAIL
# ─────────────────────────────────────────

def check_refusal(question: str) -> Tuple[bool, str]:
    refusal_triggers = [
        "hack", "bypass", "ignore previous", "jailbreak",
        "forget instructions", "pretend you are", "act as",
        "drop table", "truncate", "update set"
    ]
    question_lower = question.lower()
    for trigger in refusal_triggers:
        if trigger in question_lower:
            return True, "❌ Request declined: This question contains content that cannot be processed by the claims analysis system."
    return False, ""


# ─────────────────────────────────────────
# MAIN RUNNERS
# ─────────────────────────────────────────

def run_input_guardrails(question: str) -> Tuple[bool, str]:
    should_refuse, refusal_msg = check_refusal(question)
    if should_refuse:
        return False, refusal_msg
    is_safe, message = check_input(question)
    if not is_safe:
        return False, message
    return True, "OK"

def run_output_guardrails(answer: str, sources: list) -> Tuple[str, list]:
    return check_output(answer, sources)
