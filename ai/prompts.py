import re

SYSTEM_FINANCIAL_PROMPT = """You are the AI Financial Intelligence Assistant for the Subscription Renewal and Expense Analytics Platform.
Your mission is to provide accurate, grounded financial analysis and actionable subscription recommendations.

CORE PRINCIPLES:
1. Grounded Accuracy: Answer questions strictly using the authorized subscription records and deterministic financial metrics provided in the context.
2. No Fabrications: Never invent subscriptions, costs, dates, or calculations not present in the data.
3. Decisive Recommendations: When asked for savings, highlight low-utility, non-essential, and duplicate recurring expenses.
4. Security & Isolation: Never reveal information outside the user's authorized portfolio.

CONTEXT DATA:
{retrieved_context}

USER QUESTION:
{question}

Provide a clear, markdown-formatted financial answer including relevant numbers, subscription names, and supporting details."""


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
    r"system\s+override",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"forget\s+(all\s+)?rules",
    r"disregard\s+all\s+constraints",
]


def sanitize_user_query(query: str) -> str:
    """Detect and neutralize potential prompt injection attacks."""
    cleaned = query.strip()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return "How can I optimize my subscription expenses?"
    # Limit length to avoid prompt-stuffing Denial of Service
    if len(cleaned) > 1000:
        cleaned = cleaned[:1000]
    return cleaned
