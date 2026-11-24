from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, Numeric, Date, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship

from backend.app.models.base import Base


class RenewalStatus(str, PyEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class RenewalHistory(Base):
    __tablename__ = "renewal_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    renewal_date = Column(Date, default=date.today, nullable=False, index=True)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    status = Column(
        Enum(RenewalStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=RenewalStatus.SUCCESS,
        nullable=False
    )
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="renewal_history")

    __table_args__ = (
        Index("idx_subscription_renewal_date", "subscription_id", "renewal_date"),
    )
