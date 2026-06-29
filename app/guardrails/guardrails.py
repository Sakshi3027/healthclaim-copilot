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

OUT_OF_SCOPE_KEYWORDS = [
    "prescribe", "diagnosis", "should i take", "medical advice",
    "symptoms", "treatment", "drug", "medication", "dosage",
    "invest", "stock", "legal advice", "lawsuit", "attorney"
]

def check_input(question: str) -> Tuple[bool, str]:
    """
    Returns (is_safe, message).
    is_safe=False means block the request.
    """
    # Check for PII
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, question, re.IGNORECASE):
            return False, f"❌ Input blocked: Detected {pii_type} in your question. Please remove personal identifiable information before submitting."
    
    # Check for out-of-scope
    question_lower = question.lower()
    for keyword in OUT_OF_SCOPE_KEYWORDS:
        if keyword in question_lower:
            return False, f"❌ Out of scope: This system analyzes insurance claims data only. Questions about medical advice, legal matters, or investments are not supported."
    
    # Check minimum length
    if len(question.strip()) < 5:
        return False, "❌ Question too short. Please provide a specific question about claims data."
    
    return True, "OK"


# ─────────────────────────────────────────
# 2. OUTPUT GUARDRAIL — Hallucination Check
# ─────────────────────────────────────────

def check_output(answer: str, sources: list) -> Tuple[str, list]:
    """
    Verifies claim IDs cited in the answer exist in retrieved sources.
    Flags any hallucinated claim IDs.
    Returns (verified_answer, warnings)
    """
    warnings = []
    
    if not sources:
        return answer, warnings
    
    # Extract all claim IDs mentioned in answer
    cited_ids = set(re.findall(r"CLM\d{5}", answer))
    
    # Get valid claim IDs from sources
    valid_ids = set(s["claim_id"] for s in sources)
    
    # Find hallucinated IDs
    hallucinated = cited_ids - valid_ids
    
    if hallucinated:
        warning_msg = f"⚠️ Verification warning: The following claim IDs were mentioned but not found in retrieved sources: {', '.join(sorted(hallucinated))}. Please verify these independently."
        warnings.append(warning_msg)
        answer = answer + f"\n\n{warning_msg}"
    
    return answer, warnings


# ─────────────────────────────────────────
# 3. REFUSAL GUARDRAIL — Graceful Decline
# ─────────────────────────────────────────

def check_refusal(question: str) -> Tuple[bool, str]:
    """
    Returns (should_refuse, refusal_message).
    """
    refusal_triggers = [
        "hack", "bypass", "ignore previous", "jailbreak",
        "forget instructions", "pretend you are", "act as",
        "delete", "drop table", "truncate", "update set"
    ]
    
    question_lower = question.lower()
    for trigger in refusal_triggers:
        if trigger in question_lower:
            return True, "❌ Request declined: This question contains content that cannot be processed by the claims analysis system."
    
    return False, ""


# ─────────────────────────────────────────
# MAIN GUARDRAIL RUNNER
# ─────────────────────────────────────────

def run_input_guardrails(question: str) -> Tuple[bool, str]:
    """Run all input checks. Returns (passed, message)."""
    
    # Refusal check first
    should_refuse, refusal_msg = check_refusal(question)
    if should_refuse:
        return False, refusal_msg
    
    # PII + scope check
    is_safe, message = check_input(question)
    if not is_safe:
        return False, message
    
    return True, "OK"

def run_output_guardrails(answer: str, sources: list) -> Tuple[str, list]:
    """Run all output checks. Returns (verified_answer, warnings)."""
    return check_output(answer, sources)
