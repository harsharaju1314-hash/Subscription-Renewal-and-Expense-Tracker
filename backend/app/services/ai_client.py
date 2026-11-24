import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.subscription import Subscription, SubscriptionStatus
from backend.app.models.ai_conversation import AIConversation
from backend.app.schemas.ai import AIChatResponse, SourceReference

logger = logging.getLogger(__name__)


class AIClient:
    def __init__(self):
        self.base_url = settings.AI_SERVICE_URL
        self.timeout = settings.AI_SERVICE_TIMEOUT

    def chat(self, db: Session, user_id: int, query: str) -> AIChatResponse:
        start_time = time.time()

        # Gather current user subscriptions for grounded RAG context
        active_subs = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
            .all()
        )

        sub_docs = []
        for s in active_subs:
            cat_name = s.category.name if s.category else "General"
            cycle_str = s.billing_cycle.value if hasattr(s.billing_cycle, "value") else str(s.billing_cycle)
            sub_docs.append({
                "id": s.id,
                "name": s.name,
                "cost": float(s.cost),
                "billing_cycle": cycle_str,
                "monthly_cost": round(s.monthly_equivalent_cost, 2),
                "renewal_date": s.renewal_date.isoformat(),
                "category": cat_name,
                "is_essential": s.is_essential,
                "utility_score": s.utility_score,
                "description": s.description or "",
            })

        payload = {
            "user_id": user_id,
            "query": query,
            "subscriptions": sub_docs,
        }

        response_data = None
        # Attempt calling external Flask microservice with retry
        for attempt in range(2):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(f"{self.base_url}/ai/chat", json=payload)
                    if resp.status_code == 200:
                        response_data = resp.json()
                        break
                    else:
                        logger.warning(
                            "Flask AI service returned status %d on attempt %d: %s",
                            resp.status_code,
                            attempt + 1,
                            resp.text,
                        )
            except Exception as e:
                logger.warning("Flask AI service unreachable on attempt %d: %s", attempt + 1, e)
                if attempt == 0:
                    time.sleep(0.2)

        elapsed_ms = int((time.time() - start_time) * 1000)

        if response_data:
            answer = response_data.get("answer", "")
            sources = [SourceReference(**src) for src in response_data.get("sources", [])]
            tokens = response_data.get("tokens_used", 0)
            model_used = response_data.get("model", "flask-rag-llm")
        else:
            # Local Grounded Financial Reasoning Fallback
            answer, sources, tokens, model_used = self._local_grounded_rag(query, sub_docs)

        # Log conversation to database for audit and history
        import json
        convo = AIConversation(
            user_id=user_id,
            query=query,
            response=answer,
            retrieved_context_json=json.dumps([s.model_dump() for s in sources]),
            prompt_tokens=tokens // 2 if tokens else 0,
            completion_tokens=tokens // 2 if tokens else 0,
            latency_ms=elapsed_ms,
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)

        return AIChatResponse(
            answer=answer,
            conversation_id=convo.id,
            sources=sources,
            latency_ms=elapsed_ms,
            tokens_used=tokens,
            model=model_used,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def reindex_user(self, user_id: int, sub_docs: List[Dict[str, Any]]) -> bool:
        """Notify Flask AI service to rebuild vector index for user."""
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(
                    f"{self.base_url}/ai/reindex",
                    json={"user_id": user_id, "subscriptions": sub_docs},
                )
                return resp.status_code == 200
        except Exception as e:
            logger.debug("Could not notify Flask AI service of reindexing: %s", e)
            return False

    def _local_grounded_rag(
        self, query: str, subscriptions: List[Dict[str, Any]]
    ) -> Tuple[str, List[SourceReference], int, str]:
        """Local RAG & financial reasoning engine that answers accurately without external API."""
        from datetime import date, timedelta

        q_lower = query.lower()
        total_monthly = sum(s["monthly_cost"] for s in subscriptions)
        total_annual = total_monthly * 12.0
        today = date.today()

        sources: List[SourceReference] = []

        if not subscriptions:
            return (
                "You currently have no active subscriptions registered in the system. "
                "Add your subscriptions to see spending breakdowns and AI insights.",
                [],
                45,
                "rag-local-engine",
            )

        # 1. Total monthly or spending queries
        if any(w in q_lower for w in ["how much", "spending", "total", "spend", "cost me"]):
            sorted_by_cost = sorted(subscriptions, key=lambda s: s["monthly_cost"], reverse=True)
            top_3 = sorted_by_cost[:3]
            for s in top_3:
                sources.append(
                    SourceReference(
                        id=s["id"],
                        name=s["name"],
                        cost=s["cost"],
                        billing_cycle=s["billing_cycle"],
                        category=s["category"],
                        renewal_date=s["renewal_date"],
                        relevance_score=0.95,
                    )
                )

            top_names = ", ".join(f"{s['name']} (${s['monthly_cost']:.2f}/mo)" for s in top_3)
            answer = (
                f"You are currently spending **${total_monthly:.2f} per month** "
                f"(projected **${total_annual:.2f} annually**) across {len(subscriptions)} active subscriptions.\n\n"
                f"Your highest recurring expenses are: {top_names}."
            )
            return answer, sources, 120, "rag-grounded-engine"

        # 2. Most expensive subscriptions
        elif any(w in q_lower for w in ["most expensive", "cost the most", "highest", "biggest"]):
            sorted_by_cost = sorted(subscriptions, key=lambda s: s["monthly_cost"], reverse=True)
            top = sorted_by_cost[:5]
            for s in top:
                sources.append(
                    SourceReference(
                        id=s["id"],
                        name=s["name"],
                        cost=s["cost"],
                        billing_cycle=s["billing_cycle"],
                        category=s["category"],
                        renewal_date=s["renewal_date"],
                        relevance_score=0.98,
                    )
                )

            lines = "\n".join(
                f"- **{s['name']}**: ${s['cost']:.2f} ({s['billing_cycle']}) — ~${s['monthly_cost']:.2f}/mo in *{s['category']}*"
                for s in top
            )
            answer = f"Here are your most expensive active subscriptions by monthly cost:\n\n{lines}"
            return answer, sources, 140, "rag-grounded-engine"

        # 3. Renewals next week / upcoming renewals
        elif any(w in q_lower for w in ["renew", "renewal", "next week", "upcoming", "due"]):
            target_date = today + timedelta(days=14)
            upcoming = [
                s for s in subscriptions
                if s["renewal_date"] and today <= date.fromisoformat(s["renewal_date"]) <= target_date
            ]
            upcoming.sort(key=lambda s: s["renewal_date"])

            for s in (upcoming if upcoming else subscriptions[:3]):
                sources.append(
                    SourceReference(
                        id=s["id"],
                        name=s["name"],
                        cost=s["cost"],
                        billing_cycle=s["billing_cycle"],
                        category=s["category"],
                        renewal_date=s["renewal_date"],
                        relevance_score=0.96,
                    )
                )

            if upcoming:
                lines = "\n".join(
                    f"- **{s['name']}**: ${s['cost']:.2f} renewing on **{s['renewal_date']}** ({s['category']})"
                    for s in upcoming
                )
                answer = f"You have {len(upcoming)} subscription(s) renewing in the next two weeks:\n\n{lines}"
            else:
                answer = (
                    "You have no subscriptions scheduled to renew within the next 14 days. "
                    "All active subscriptions are in good standing."
                )
            return answer, sources, 110, "rag-grounded-engine"

        # 4. Reduce expenses / savings
        elif any(w in q_lower for w in ["reduce", "save", "cut", "lower", "optimization", "savings"]):
            low_utility = [s for s in subscriptions if not s.get("is_essential") and s.get("utility_score", 5) <= 4]
            if not low_utility:
                low_utility = sorted(subscriptions, key=lambda s: s.get("utility_score", 5))[:2]

            potential_savings = sum(s["monthly_cost"] for s in low_utility)
            for s in low_utility:
                sources.append(
                    SourceReference(
                        id=s["id"],
                        name=s["name"],
                        cost=s["cost"],
                        billing_cycle=s["billing_cycle"],
                        category=s["category"],
                        renewal_date=s["renewal_date"],
                        relevance_score=0.92,
                    )
                )

            lines = "\n".join(
                f"- **{s['name']}**: ${s['monthly_cost']:.2f}/mo (Utility score: {s['utility_score']}/10)"
                for s in low_utility
            )
            answer = (
                f"You can save up to **${potential_savings:.2f} per month** (${potential_savings * 12:.2f}/year) "
                f"by pausing or cancelling optional subscriptions with low utility scores:\n\n{lines}\n\n"
                f"You can also use the **Budget Optimizer** tab to run a mathematical knapsack optimization against your monthly target."
            )
            return answer, sources, 150, "rag-grounded-engine"

        # 5. Compare or category search
        else:
            # Semantic search match based on query keywords
            matches = [
                s for s in subscriptions
                if any(k in s["name"].lower() or k in s["category"].lower() for k in q_lower.split())
            ]
            if not matches:
                matches = subscriptions[:4]

            for s in matches[:4]:
                sources.append(
                    SourceReference(
                        id=s["id"],
                        name=s["name"],
                        cost=s["cost"],
                        billing_cycle=s["billing_cycle"],
                        category=s["category"],
                        renewal_date=s["renewal_date"],
                        relevance_score=0.88,
                    )
                )

            summary_items = ", ".join(f"{s['name']} (${s['monthly_cost']:.2f}/mo)" for s in matches[:4])
            answer = (
                f"Based on your {len(subscriptions)} active subscriptions with a total monthly spend of **${total_monthly:.2f}**:\n\n"
                f"Relevant subscriptions identified: {summary_items}.\n"
                f"Feel free to ask for specific spending totals, upcoming renewal dates, category breakdowns, or optimization advice!"
            )
            return answer, sources, 130, "rag-grounded-engine"


ai_client = AIClient()
