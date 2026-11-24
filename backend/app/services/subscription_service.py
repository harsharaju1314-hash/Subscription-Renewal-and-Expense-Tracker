from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from backend.app.models.subscription import Subscription, SubscriptionStatus, BillingCycle
from backend.app.models.category import Category
from backend.app.models.renewal_history import RenewalHistory, RenewalStatus
from backend.app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    RenewalNoticeResponse,
)
from backend.app.core.cache import cache


def _format_subscription_response(sub: Subscription) -> SubscriptionResponse:
    today = date.today()
    days_left = (sub.renewal_date - today).days
    
    return SubscriptionResponse(
        id=sub.id,
        user_id=sub.user_id,
        category_id=sub.category_id,
        name=sub.name,
        description=sub.description,
        cost=sub.cost,
        currency=sub.currency,
        billing_cycle=sub.billing_cycle,
        start_date=sub.start_date,
        renewal_date=sub.renewal_date,
        status=sub.status,
        auto_renew=sub.auto_renew,
        payment_method=sub.payment_method,
        cancellation_url=sub.cancellation_url,
        utility_score=sub.utility_score,
        is_essential=sub.is_essential,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
        category=sub.category,
        monthly_equivalent_cost=round(sub.monthly_equivalent_cost, 2),
        annual_equivalent_cost=round(sub.annual_equivalent_cost, 2),
        days_until_renewal=days_left,
    )


class SubscriptionService:

    @staticmethod
    def get_subscriptions(
        db: Session,
        user_id: int,
        status: Optional[SubscriptionStatus] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = "renewal_date",
        order: Optional[str] = "asc"
    ) -> List[SubscriptionResponse]:
        query = db.query(Subscription).filter(Subscription.user_id == user_id)

        if status:
            query = query.filter(Subscription.status == status)
        if category_id:
            query = query.filter(Subscription.category_id == category_id)
        if search:
            search_fmt = f"%{search}%"
            query = query.filter(
                or_(
                    Subscription.name.ilike(search_fmt),
                    Subscription.description.ilike(search_fmt),
                    Subscription.payment_method.ilike(search_fmt),
                )
            )

        # Sorting
        sort_column = getattr(Subscription, sort_by, Subscription.renewal_date)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        subscriptions = query.all()
        return [_format_subscription_response(sub) for sub in subscriptions]

    @staticmethod
    def get_subscription_by_id(db: Session, sub_id: int, user_id: int) -> Optional[Subscription]:
        # Strict user-level isolation: only return if user_id matches
        return (
            db.query(Subscription)
            .filter(Subscription.id == sub_id, Subscription.user_id == user_id)
            .first()
        )

    @staticmethod
    def create_subscription(db: Session, sub_in: SubscriptionCreate, user_id: int) -> SubscriptionResponse:
        sub = Subscription(
            user_id=user_id,
            category_id=sub_in.category_id,
            name=sub_in.name,
            description=sub_in.description,
            cost=sub_in.cost,
            currency=sub_in.currency,
            billing_cycle=sub_in.billing_cycle,
            start_date=sub_in.start_date,
            renewal_date=sub_in.renewal_date,
            status=sub_in.status,
            auto_renew=sub_in.auto_renew,
            payment_method=sub_in.payment_method,
            cancellation_url=sub_in.cancellation_url,
            utility_score=sub_in.utility_score,
            is_essential=sub_in.is_essential,
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)

        # Invalidate cached analytics & list
        cache.invalidate_user_cache(user_id)

        return _format_subscription_response(sub)

    @staticmethod
    def update_subscription(
        db: Session, sub_id: int, sub_in: SubscriptionUpdate, user_id: int
    ) -> Optional[SubscriptionResponse]:
        sub = SubscriptionService.get_subscription_by_id(db, sub_id, user_id)
        if not sub:
            return None

        update_data = sub_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sub, field, value)

        db.commit()
        db.refresh(sub)

        # Invalidate cache
        cache.invalidate_user_cache(user_id)

        return _format_subscription_response(sub)

    @staticmethod
    def delete_subscription(db: Session, sub_id: int, user_id: int) -> bool:
        sub = SubscriptionService.get_subscription_by_id(db, sub_id, user_id)
        if not sub:
            return False

        db.delete(sub)
        db.commit()

        # Invalidate cache
        cache.invalidate_user_cache(user_id)

        return True

    @staticmethod
    def get_upcoming_renewals(
        db: Session, user_id: int, days_ahead: int = 30
    ) -> List[RenewalNoticeResponse]:
        today = date.today()
        target_date = today + timedelta(days=days_ahead)

        subscriptions = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.renewal_date >= today,
                Subscription.renewal_date <= target_date,
            )
            .order_by(Subscription.renewal_date.asc())
            .all()
        )

        results = []
        for sub in subscriptions:
            days_left = (sub.renewal_date - today).days
            cat_name = sub.category.name if sub.category else "Uncategorized"
            cycle_str = sub.billing_cycle.value if hasattr(sub.billing_cycle, "value") else str(sub.billing_cycle)
            status_str = sub.status.value if hasattr(sub.status, "value") else str(sub.status)
            results.append(
                RenewalNoticeResponse(
                    id=sub.id,
                    name=sub.name,
                    cost=float(sub.cost),
                    currency=sub.currency,
                    billing_cycle=cycle_str,
                    renewal_date=sub.renewal_date,
                    days_left=days_left,
                    category_name=cat_name,
                    is_essential=sub.is_essential,
                    status=status_str,
                )
            )
        return results
