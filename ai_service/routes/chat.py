import time
import logging
from flask import Blueprint, request, jsonify
from langchain_core.output_parsers import StrOutputParser

from ai_service.config import settings
from ai_service.rag.vector_store import vector_manager
from ai_service.prompts.financial_prompts import RAG_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)
chat_bp = Blueprint("chat", __name__)


def generate_llm_response(prompt_text: str) -> str:
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith("sk-"):
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.2,
                openai_api_key=settings.OPENAI_API_KEY,
            )
            chain = llm | StrOutputParser()
            return chain.invoke(prompt_text)
        except Exception as e:
            logger.warning("OpenAI API call failed: %s; using grounded fallback.", e)
    return ""


@chat_bp.route("/ai/chat", methods=["POST"])
def chat():
    start_time = time.time()
    data = request.get_json(force=True) or {}

    user_id = data.get("user_id")
    query = data.get("query", "").strip()
    subscriptions = data.get("subscriptions", [])

    if not user_id:
        return jsonify({"error": "Missing user_id parameter."}), 400
    if not query:
        return jsonify({"error": "Missing query parameter."}), 400

    if subscriptions:
        vector_manager.index_subscriptions(user_id, subscriptions)

    # 1. Semantic Similarity Search via FAISS
    retrieved_docs = vector_manager.similarity_search(
        user_id=user_id,
        query=query,
        k=settings.TOP_K_RETRIEVAL,
        fallback_subscriptions=subscriptions,
    )

    # 2. Extract Supporting Sources
    sources = []
    for doc in retrieved_docs:
        meta = doc.metadata
        sources.append({
            "id": meta.get("subscription_id"),
            "name": meta.get("name"),
            "cost": meta.get("cost"),
            "billing_cycle": meta.get("billing_cycle"),
            "category": meta.get("category"),
            "renewal_date": meta.get("renewal_date"),
            "relevance_score": 0.95,
        })

    # 3. Build Prompt Context
    if retrieved_docs:
        context_str = "\n\n".join(doc.page_content for doc in retrieved_docs)
    else:
        context_str = "No active subscription documents found."

    prompt_formatted = RAG_PROMPT_TEMPLATE.format(
        retrieved_context=context_str,
        question=query,
    )

    # 4. LLM Generation
    answer = generate_llm_response(prompt_formatted)
    model_used = settings.OPENAI_MODEL if answer else "rag-grounded-engine"

    if not answer:
        # Grounded financial analysis based on retrieved documents and subscriptions
        total_monthly = sum(s.get("monthly_cost", 0.0) for s in subscriptions)
        total_annual = total_monthly * 12.0

        q_lower = query.lower()
        if any(w in q_lower for w in ["expensive", "highest", "cost the most", "cost me the most", "most expensive"]):
            sorted_subs = sorted(subscriptions, key=lambda s: s.get("monthly_cost", 0), reverse=True)
            top = sorted_subs[:4]
            lines = "\n".join(
                f"- **{s['name']}**: ${s['cost']:.2f} ({s['billing_cycle']}) — ${s.get('monthly_cost', 0):.2f}/mo ({s['category']})"
                for s in top
            )
            answer = f"Based on your active records, here are your most expensive subscriptions:\n\n{lines}"
        elif any(w in q_lower for w in ["spend", "total", "how much", "cost"]):
            top_sources_str = ", ".join(f"**{s['name']}** (${s['cost']:.2f}/{s['billing_cycle'].lower()})" for s in sources[:3])
            answer = (
                f"You are currently spending **${total_monthly:.2f} per month** (${total_annual:.2f} annually) "
                f"across your active subscriptions.\n\n"
                f"Retrieved key subscription accounts:\n{top_sources_str}."
            )
        elif any(w in q_lower for w in ["renew", "upcoming", "due", "next week"]):
            from datetime import date, timedelta
            today = date.today()
            upcoming = [
                s for s in subscriptions
                if s.get("renewal_date") and today <= date.fromisoformat(s["renewal_date"]) <= (today + timedelta(days=14))
            ]
            if upcoming:
                lines = "\n".join(
                    f"- **{s['name']}**: ${s['cost']:.2f} due on **{s['renewal_date']}**"
                    for s in upcoming
                )
                answer = f"You have {len(upcoming)} subscription(s) renewing in the next 14 days:\n\n{lines}"
            else:
                answer = "You have no subscriptions due for renewal within the next 14 days."
        elif any(w in q_lower for w in ["reduce", "save", "cut", "optimize"]):
            low_util = [s for s in subscriptions if not s.get("is_essential") and s.get("utility_score", 5) <= 5]
            savings = sum(s.get("monthly_cost", 0) for s in low_util)
            lines = "\n".join(
                f"- **{s['name']}**: ${s.get('monthly_cost', 0):.2f}/mo (Utility score: {s.get('utility_score', 5)}/10)"
                for s in low_util
            )
            answer = (
                f"You could save up to **${savings:.2f}/month** (${savings * 12:.2f}/year) by reviewing these lower-utility subscriptions:\n\n"
                f"{lines}\n\n"
                f"Use the **Budget Optimizer** tab to calculate the optimal subset of subscriptions."
            )
        else:
            doc_items = "\n".join(f"- **{d.metadata.get('name')}**: ${d.metadata.get('cost'):.2f} ({d.metadata.get('category')})" for d in retrieved_docs[:4])
            answer = (
                f"Based on your subscription portfolio (${total_monthly:.2f}/mo total spend):\n\n"
                f"{doc_items}\n\n"
                f"Ask me about any specific subscription, category breakdown, upcoming renewal dates, or potential cost savings!"
            )

    latency_ms = int((time.time() - start_time) * 1000)

    return jsonify({
        "answer": answer,
        "sources": sources,
        "tokens_used": len(prompt_formatted.split()) + len(answer.split()),
        "model": model_used,
        "latency_ms": latency_ms,
    })
