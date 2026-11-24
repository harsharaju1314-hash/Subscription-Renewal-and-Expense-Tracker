from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship

from backend.app.models.base import Base


class PaymentStatus(str, PyEnum):
    PAID = "PAID"
    PENDING = "PENDING"
    FAILED = "FAILED"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)

    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    expense_date = Column(Date, default=date.today, nullable=False, index=True)
    payment_status = Column(
        Enum(PaymentStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=PaymentStatus.PAID,
        nullable=False
    )
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="expenses")
    subscription = relationship("Subscription", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")

    __table_args__ = (
        Index("idx_user_expense_date", "user_id", "expense_date"),
    )
