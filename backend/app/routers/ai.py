from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.ai_conversation import AIConversation
from backend.app.schemas.ai import AIChatRequest, AIChatResponse
from backend.app.services.ai_client import ai_client
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Financial Assistant"])


@router.post("/chat", response_model=AIChatResponse)
@router.post("/query", response_model=AIChatResponse)
def chat_with_assistant(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Interact with the RAG-powered Financial Assistant grounded on user subscription data."""
    try:
        return ai_client.chat(db=db, user_id=current_user.id, query=request.query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI inference error: {str(e)}",
        )


@router.get("/history")
def get_conversation_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve recent AI conversation history for the current user."""
    convos = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == current_user.id)
        .order_by(desc(AIConversation.created_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": c.id,
            "query": c.query,
            "response": c.response,
            "latency_ms": c.latency_ms,
            "created_at": c.created_at.isoformat(),
        }
        for c in convos
    ]
