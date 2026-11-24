from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship

from backend.app.models.base import Base


class ReminderStatus(str, PyEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    DISMISSED = "DISMISSED"


class RenewalReminder(Base):
    __tablename__ = "renewal_reminders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)

    reminder_date = Column(Date, nullable=False, index=True)
    days_before = Column(Integer, default=3, nullable=False)
    channel = Column(String(50), default="EMAIL", nullable=False)
    is_sent = Column(Boolean, default=False, nullable=False)
    status = Column(
        Enum(ReminderStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=ReminderStatus.PENDING,
        nullable=False
    )
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="renewal_reminders")
    subscription = relationship("Subscription", back_populates="renewal_reminders")

    __table_args__ = (
        Index("idx_reminder_user_date", "user_id", "reminder_date", "status"),
    )
