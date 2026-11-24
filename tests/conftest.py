import os
import sys

# Prevent hanging on optional transformers package scans in isolated environment
sys.modules["transformers"] = None

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../ai-service")))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-testing-32-chars-long"
os.environ["ENVIRONMENT"] = "testing"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["ANONYMIZED_TELEMETRY"] = "false"

# Pre-load C-extensions on main thread before runner redirects handles
try:
    import faiss
except Exception:
    pass

from backend.app.core.config import settings
settings.ENVIRONMENT = "testing"
settings.DATABASE_URL = "sqlite:///:memory:"

from backend.app.core.database import Base, get_db
from backend.app.main import app, seed_default_categories
from backend.app.models.user import User
from backend.app.models.category import Category
from backend.app.models.subscription import Subscription, BillingCycle, SubscriptionStatus
from backend.app.models.budget import Budget
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.core.cache import cache

from ai_service.main import create_app as create_flask_app


# In-memory SQLite engine with StaticPool so all threads share test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    # Seed default categories
    default_cats = [
        {"name": "Streaming", "icon": "live_tv", "color": "#ef4444"},
        {"name": "Developer Tools", "icon": "code", "color": "#6366f1"},
        {"name": "Productivity", "icon": "work", "color": "#f59e0b"},
        {"name": "Cloud", "icon": "cloud", "color": "#0ea5e9"},
    ]
    for c in default_cats:
        db.add(Category(**c))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def flask_client():
    flask_app = create_flask_app()
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def test_user(db_session) -> User:
    user = db_session.query(User).filter(User.username == "testuser").first()
    if not user:
        user = User(
            email="testuser@tracker.ai",
            username="testuser",
            hashed_password=get_password_hash("TestPassword123!"),
            full_name="Test User",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        budget = db_session.query(Budget).filter(Budget.user_id == user.id).first()
        if not budget:
            budget = Budget(user_id=user.id, monthly_limit=200.00, alert_threshold_pct=80)
            db_session.add(budget)
            db_session.commit()
    
    # Reset user subscriptions to clean state for each test
    db_session.query(Subscription).filter(Subscription.user_id == user.id).delete()
    db_session.commit()
    return user


@pytest.fixture
def second_user(db_session) -> User:
    user = db_session.query(User).filter(User.username == "otheruser").first()
    if not user:
        user = User(
            email="otheruser@tracker.ai",
            username="otheruser",
            hashed_password=get_password_hash("TestPassword123!"),
            full_name="Other User",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    db_session.query(Subscription).filter(Subscription.user_id == user.id).delete()
    db_session.commit()
    return user


@pytest.fixture
def user_token(test_user) -> str:
    return create_access_token(subject=test_user.id)


@pytest.fixture
def second_user_token(second_user) -> str:
    return create_access_token(subject=second_user.id)


@pytest.fixture
def auth_headers(user_token) -> dict:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def second_user_headers(second_user_token) -> dict:
    return {"Authorization": f"Bearer {second_user_token}"}


@pytest.fixture
def sample_subscription(db_session, test_user) -> Subscription:
    cat = db_session.query(Category).first()
    sub = Subscription(
        user_id=test_user.id,
        category_id=cat.id,
        name="Netflix 4K",
        cost=Decimal("22.99"),
        currency="USD",
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today() - timedelta(days=60),
        renewal_date=date.today() + timedelta(days=10),
        status=SubscriptionStatus.ACTIVE,
        auto_renew=True,
        payment_method="Visa ****4242",
        utility_score=8,
        is_essential=False,
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    return sub
