from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship

from backend.app.models.base import Base


class BillingCycle(str, PyEnum):
    MONTHLY = "MONTHLY"
    ANNUAL = "ANNUAL"
    QUARTERLY = "QUARTERLY"
    WEEKLY = "WEEKLY"


class SubscriptionStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    PAUSED = "PAUSED"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)

    name = Column(String(150), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    cost = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    billing_cycle = Column(
        Enum(BillingCycle, values_callable=lambda obj: [e.value for e in obj]),
        default=BillingCycle.MONTHLY,
        nullable=False
    )
    start_date = Column(Date, default=date.today, nullable=False)
    renewal_date = Column(Date, nullable=False, index=True)
    status = Column(
        Enum(SubscriptionStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
        index=True
    )
    auto_renew = Column(Boolean, default=True, nullable=False)
    payment_method = Column(String(100), nullable=True)
    cancellation_url = Column(String(255), nullable=True)

    # Optimization fields
    utility_score = Column(Integer, default=5, nullable=False)  # 1 (low value) to 10 (critical)
    is_essential = Column(Boolean, default=False, nullable=False)  # True = cannot be cut in optimizer

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    category = relationship("Category", back_populates="subscriptions")
    expenses = relationship("Expense", back_populates="subscription", cascade="all, delete-orphan")
    renewal_history = relationship("RenewalHistory", back_populates="subscription", cascade="all, delete-orphan")
    renewal_reminders = relationship("RenewalReminder", back_populates="subscription", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_status_renewal", "user_id", "status", "renewal_date"),
    )

    @property
    def monthly_equivalent_cost(self) -> float:
        """Normalize cost to monthly expense for standardized analytics and budgeting."""
        raw_cost = float(self.cost)
        cycle = self.billing_cycle.value if hasattr(self.billing_cycle, "value") else str(self.billing_cycle)
        if cycle == BillingCycle.MONTHLY.value:
            return raw_cost
        elif cycle == BillingCycle.ANNUAL.value:
            return raw_cost / 12.0
        elif cycle == BillingCycle.QUARTERLY.value:
            return raw_cost / 3.0
        elif cycle == BillingCycle.WEEKLY.value:
            return (raw_cost * 52.0) / 12.0
        return raw_cost

    @property
    def annual_equivalent_cost(self) -> float:
        """Normalize cost to annual expense."""
        return self.monthly_equivalent_cost * 12.0
