import numpy as np
from ai_service.rag.document_loader import format_subscription_to_document
from ai_service.rag.embedder import DeterministicFinancialEmbeddings
from ai_service.rag.vector_store import FAISSVectorStoreManager


def test_format_subscription_to_document():
    raw_sub = {
        "id": 42,
        "name": "ChatGPT Plus",
        "cost": 20.0,
        "monthly_cost": 20.0,
        "billing_cycle": "MONTHLY",
        "category": "AI Tools",
        "renewal_date": "2026-12-01",
        "utility_score": 10,
        "is_essential": True,
        "description": "GPT-4o access and coding assistant",
    }
    doc = format_subscription_to_document(raw_sub, user_id=12)
    assert "ChatGPT Plus" in doc.page_content
    assert "20.00" in doc.page_content
    assert "Essential" in doc.page_content
    assert doc.metadata["user_id"] == 12
    assert doc.metadata["subscription_id"] == 42


def test_deterministic_embeddings_shape_and_norm():
    embedder = DeterministicFinancialEmbeddings(dimension=1536)
    vec = embedder.embed_query("Netflix streaming subscription renewal")
    assert len(vec) == 1536
    # Unit vector norm should be approximately 1.0
    norm = np.linalg.norm(np.array(vec))
    assert abs(norm - 1.0) < 1e-4


def test_faiss_vector_store_indexing(tmp_path):
    mgr = FAISSVectorStoreManager()
    mgr_dir = str(tmp_path / "faiss_test")
    from ai_service.config import settings
    settings.FAISS_INDEX_DIR = mgr_dir

    subs = [
        {"id": 1, "name": "Netflix", "cost": 15.49, "monthly_cost": 15.49, "category": "Streaming"},
        {"id": 2, "name": "Spotify", "cost": 10.99, "monthly_cost": 10.99, "category": "Music"},
    ]
    count = mgr.index_subscriptions(user_id=88, subscriptions=subs)
    assert count == 2


def test_faiss_semantic_similarity_search():
    mgr = FAISSVectorStoreManager()
    subs = [
        {"id": 101, "name": "Amazon Prime Video", "cost": 14.99, "monthly_cost": 14.99, "category": "Streaming"},
        {"id": 102, "name": "JetBrains IDE", "cost": 29.00, "monthly_cost": 29.00, "category": "Developer"},
        {"id": 103, "name": "Apple Music", "cost": 10.99, "monthly_cost": 10.99, "category": "Music"},
    ]
    mgr.index_subscriptions(user_id=55, subscriptions=subs)

    # Search for streaming
    results = mgr.similarity_search(user_id=55, query="video streaming movies", k=2)
    assert len(results) > 0
    top_name = results[0].metadata["name"]
    assert "Amazon Prime Video" in top_name


def test_reindex_on_subscription_modification():
    mgr = FAISSVectorStoreManager()
    subs = [
        {"id": 201, "name": "Old Gym Pass", "cost": 25.0, "monthly_cost": 25.0, "category": "Fitness"}
    ]
    mgr.index_subscriptions(user_id=66, subscriptions=subs)
    res1 = mgr.similarity_search(user_id=66, query="Gym Pass")
    assert len(res1) == 1

    # Modify / Reindex without the gym pass
    updated_subs = [
        {"id": 202, "name": "Climbing Club", "cost": 45.0, "monthly_cost": 45.0, "category": "Fitness"}
    ]
    mgr.index_subscriptions(user_id=66, subscriptions=updated_subs)
    res2 = mgr.similarity_search(user_id=66, query="Climbing Club")
    assert len(res2) == 1
    assert res2[0].metadata["name"] == "Climbing Club"
