import os
import sys
import random
from datetime import date, timedelta
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from backend.app.models.category import Category
from backend.app.models.subscription import Subscription, BillingCycle, SubscriptionStatus
from backend.app.models.expense import Expense, PaymentStatus
from backend.app.models.budget import Budget
from backend.app.models.renewal_history import RenewalHistory, RenewalStatus


REALISTIC_CATALOG = [
    # Streaming & Entertainment
    {"name": "Netflix Premium", "cat": "Streaming & Entertainment", "cost": 22.99, "cycle": BillingCycle.MONTHLY, "util": 8, "ess": False},
    {"name": "Netflix Standard", "cat": "Streaming & Entertainment", "cost": 15.49, "cycle": BillingCycle.MONTHLY, "util": 7, "ess": False},
    {"name": "Amazon Prime", "cat": "Streaming & Entertainment", "cost": 139.00, "cycle": BillingCycle.ANNUAL, "util": 9, "ess": True},
    {"name": "Disney+ Bundle", "cat": "Streaming & Entertainment", "cost": 14.99, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "HBO Max (Max)", "cat": "Streaming & Entertainment", "cost": 15.99, "cycle": BillingCycle.MONTHLY, "util": 7, "ess": False},
    {"name": "Hulu (No Ads)", "cat": "Streaming & Entertainment", "cost": 17.99, "cycle": BillingCycle.MONTHLY, "util": 5, "ess": False},
    {"name": "Apple TV+", "cat": "Streaming & Entertainment", "cost": 9.99, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "Paramount+ with Showtime", "cat": "Streaming & Entertainment", "cost": 11.99, "cycle": BillingCycle.MONTHLY, "util": 4, "ess": False},
    {"name": "Peacock Premium", "cat": "Streaming & Entertainment", "cost": 5.99, "cycle": BillingCycle.MONTHLY, "util": 4, "ess": False},
    {"name": "Crunchyroll Mega Fan", "cat": "Streaming & Entertainment", "cost": 9.99, "cycle": BillingCycle.MONTHLY, "util": 5, "ess": False},

    # Music & Audio
    {"name": "Spotify Premium", "cat": "Music & Audio", "cost": 11.99, "cycle": BillingCycle.MONTHLY, "util": 9, "ess": True},
    {"name": "Apple Music", "cat": "Music & Audio", "cost": 10.99, "cycle": BillingCycle.MONTHLY, "util": 8, "ess": False},
    {"name": "YouTube Premium", "cat": "Music & Audio", "cost": 13.99, "cycle": BillingCycle.MONTHLY, "util": 9, "ess": True},
    {"name": "Audible Premium Plus", "cat": "Music & Audio", "cost": 14.95, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "Tidal HiFi Plus", "cat": "Music & Audio", "cost": 10.99, "cycle": BillingCycle.MONTHLY, "util": 5, "ess": False},
    {"name": "SoundCloud Go+", "cat": "Music & Audio", "cost": 9.99, "cycle": BillingCycle.MONTHLY, "util": 4, "ess": False},

    # Software & Developer Tools
    {"name": "GitHub Copilot Individual", "cat": "Software & Developer Tools", "cost": 10.00, "cycle": BillingCycle.MONTHLY, "util": 10, "ess": True},
    {"name": "ChatGPT Plus", "cat": "Software & Developer Tools", "cost": 20.00, "cycle": BillingCycle.MONTHLY, "util": 10, "ess": True},
    {"name": "JetBrains All Products Pack", "cat": "Software & Developer Tools", "cost": 289.00, "cycle": BillingCycle.ANNUAL, "util": 9, "ess": True},
    {"name": "Claude Pro", "cat": "Software & Developer Tools", "cost": 20.00, "cycle": BillingCycle.MONTHLY, "util": 9, "ess": True},
    {"name": "Docker Pro", "cat": "Software & Developer Tools", "cost": 5.00, "cycle": BillingCycle.MONTHLY, "util": 7, "ess": False},
    {"name": "Postman Pro", "cat": "Software & Developer Tools", "cost": 14.00, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "Cursor Pro", "cat": "Software & Developer Tools", "cost": 20.00, "cycle": BillingCycle.MONTHLY, "util": 9, "ess": True},
    {"name": "GitKraken Pro", "cat": "Software & Developer Tools", "cost": 59.00, "cycle": BillingCycle.ANNUAL, "util": 5, "ess": False},

    # Cloud & Infrastructure
    {"name": "AWS Cloud Dev Tier", "cat": "Cloud & Infrastructure", "cost": 45.00, "cycle": BillingCycle.MONTHLY, "util": 9, "ess": True},
    {"name": "Vercel Pro", "cat": "Cloud & Infrastructure", "cost": 20.00, "cycle": BillingCycle.MONTHLY, "util": 8, "ess": True},
    {"name": "DigitalOcean Droplets", "cat": "Cloud & Infrastructure", "cost": 24.00, "cycle": BillingCycle.MONTHLY, "util": 8, "ess": False},
    {"name": "Cloudflare Pro", "cat": "Cloud & Infrastructure", "cost": 20.00, "cycle": BillingCycle.MONTHLY, "util": 7, "ess": False},
    {"name": "Supabase Pro", "cat": "Cloud & Infrastructure", "cost": 25.00, "cycle": BillingCycle.MONTHLY, "util": 8, "ess": False},
    {"name": "Namecheap Domain & DNS", "cat": "Cloud & Infrastructure", "cost": 18.99, "cycle": BillingCycle.ANNUAL, "util": 8, "ess": True},

    # Productivity & Office
    {"name": "Notion Plus", "cat": "Productivity & Office", "cost": 10.00, "cycle": BillingCycle.MONTHLY, "util": 8, "ess": True},
    {"name": "Google Workspace Business", "cat": "Productivity & Office", "cost": 12.00, "cycle": BillingCycle.MONTHLY, "util": 9, "ess": True},
    {"name": "Microsoft 365 Family", "cat": "Productivity & Office", "cost": 99.99, "cycle": BillingCycle.ANNUAL, "util": 8, "ess": False},
    {"name": "Adobe Creative Cloud", "cat": "Productivity & Office", "cost": 54.99, "cycle": BillingCycle.MONTHLY, "util": 7, "ess": False},
    {"name": "1Password Family", "cat": "Productivity & Office", "cost": 4.99, "cycle": BillingCycle.MONTHLY, "util": 10, "ess": True},
    {"name": "Figma Professional", "cat": "Productivity & Office", "cost": 15.00, "cycle": BillingCycle.MONTHLY, "util": 7, "ess": False},
    {"name": "Grammarly Premium", "cat": "Productivity & Office", "cost": 12.00, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "Todoist Pro", "cat": "Productivity & Office", "cost": 4.00, "cycle": BillingCycle.MONTHLY, "util": 7, "ess": False},

    # Fitness & Health
    {"name": "Planet Fitness Black Card", "cat": "Fitness & Health", "cost": 24.99, "cycle": BillingCycle.MONTHLY, "util": 7, "ess": True},
    {"name": "Strava Premium", "cat": "Fitness & Health", "cost": 79.99, "cycle": BillingCycle.ANNUAL, "util": 6, "ess": False},
    {"name": "Headspace", "cat": "Fitness & Health", "cost": 69.99, "cycle": BillingCycle.ANNUAL, "util": 5, "ess": False},
    {"name": "Whoop 4.0 Membership", "cat": "Fitness & Health", "cost": 30.00, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "Peloton App One", "cat": "Fitness & Health", "cost": 12.99, "cycle": BillingCycle.MONTHLY, "util": 4, "ess": False},

    # Shopping & Delivery
    {"name": "Instacart+", "cat": "Shopping & Delivery", "cost": 99.00, "cycle": BillingCycle.ANNUAL, "util": 6, "ess": False},
    {"name": "DoorDash DashPass", "cat": "Shopping & Delivery", "cost": 9.99, "cycle": BillingCycle.MONTHLY, "util": 5, "ess": False},
    {"name": "Uber One", "cat": "Shopping & Delivery", "cost": 9.99, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "Costco Gold Star", "cat": "Shopping & Delivery", "cost": 65.00, "cycle": BillingCycle.ANNUAL, "util": 8, "ess": True},

    # News & Learning
    {"name": "The New York Times", "cat": "News & Learning", "cost": 4.00, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "Medium Membership", "cat": "News & Learning", "cost": 5.00, "cycle": BillingCycle.MONTHLY, "util": 6, "ess": False},
    {"name": "The Wall Street Journal", "cat": "News & Learning", "cost": 12.00, "cycle": BillingCycle.MONTHLY, "util": 5, "ess": False},
    {"name": "Coursera Plus", "cat": "News & Learning", "cost": 399.00, "cycle": BillingCycle.ANNUAL, "util": 7, "ess": False},
    {"name": "Duolingo Super", "cat": "News & Learning", "cost": 83.99, "cycle": BillingCycle.ANNUAL, "util": 5, "ess": False},
]

PAYMENT_METHODS = ["Visa ****4242", "Mastercard ****8819", "Amex ****1004", "PayPal (dev@account)", "Apple Pay"]


def generate_seed_data(num_records: int = 1000):
    print(f"Creating database schema and generating {num_records} synthetic subscription records...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create Categories
        categories_dict = {}
        from backend.app.main import seed_default_categories
        seed_default_categories()

        all_cats = db.query(Category).all()
        for cat in all_cats:
            categories_dict[cat.name] = cat.id

        # 2. Create Demo User
        demo_user = db.query(User).filter(User.email == "demo@tracker.ai").first()
        if not demo_user:
            demo_user = User(
                email="demo@tracker.ai",
                username="demouser",
                hashed_password=get_password_hash("Password123!"),
                full_name="Alex Mercer (Portfolio Demo)",
                is_active=True,
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            budget = Budget(user_id=demo_user.id, monthly_limit=220.00, alert_threshold_pct=80)
            db.add(budget)
            db.commit()

        # Seed 12 realistic core subscriptions specifically for demo user
        demo_subs_seed = [
            ("Netflix Premium", "Streaming & Entertainment", 22.99, BillingCycle.MONTHLY, 8, False, 12),
            ("Spotify Premium", "Music & Audio", 11.99, BillingCycle.MONTHLY, 9, True, 5),
            ("GitHub Copilot", "Software & Developer Tools", 10.00, BillingCycle.MONTHLY, 10, True, 18),
            ("ChatGPT Plus", "Software & Developer Tools", 20.00, BillingCycle.MONTHLY, 10, True, 22),
            ("AWS Cloud Dev Tier", "Cloud & Infrastructure", 38.50, BillingCycle.MONTHLY, 9, True, 14),
            ("Amazon Prime", "Shopping & Delivery", 139.00, BillingCycle.ANNUAL, 8, True, 90),
            ("Notion Plus", "Productivity & Office", 10.00, BillingCycle.MONTHLY, 8, True, 8),
            ("Adobe Creative Cloud", "Productivity & Office", 54.99, BillingCycle.MONTHLY, 4, False, 3),
            ("DoorDash DashPass", "Shopping & Delivery", 9.99, BillingCycle.MONTHLY, 3, False, 7),
            ("Gym Membership", "Fitness & Health", 29.99, BillingCycle.MONTHLY, 7, True, 25),
            ("Medium Membership", "News & Learning", 5.00, BillingCycle.MONTHLY, 4, False, 20),
            ("Paramount+", "Streaming & Entertainment", 11.99, BillingCycle.MONTHLY, 3, False, 16),
        ]

        today = date.today()
        for name, cat_name, cost, cycle, util, ess, days_ahead in demo_subs_seed:
            cat_id = categories_dict.get(cat_name, list(categories_dict.values())[0])
            exists = (
                db.query(Subscription)
                .filter(Subscription.user_id == demo_user.id, Subscription.name == name)
                .first()
            )
            if not exists:
                sub = Subscription(
                    user_id=demo_user.id,
                    category_id=cat_id,
                    name=name,
                    cost=Decimal(str(cost)),
                    currency="USD",
                    billing_cycle=cycle,
                    start_date=today - timedelta(days=random.randint(60, 360)),
                    renewal_date=today + timedelta(days=days_ahead),
                    status=SubscriptionStatus.ACTIVE,
                    auto_renew=True,
                    payment_method=random.choice(PAYMENT_METHODS),
                    utility_score=util,
                    is_essential=ess,
                    description=f"Standard personal {name} subscription.",
                )
                db.add(sub)
        db.commit()

        # 3. Create Additional Synthetic Users to reach 1,000+ total subscriptions
        users_count = db.query(User).count()
        needed_users = max(50, (num_records // 15) + 5)

        created_users = [demo_user]
        for i in range(users_count, needed_users):
            u_email = f"user_{i}@enterprise-analytics.io"
            existing_u = db.query(User).filter(User.email == u_email).first()
            if not existing_u:
                u = User(
                    email=u_email,
                    username=f"analyst_{i}",
                    hashed_password=get_password_hash("SecretPass123!"),
                    full_name=f"Synthetic User {i}",
                    is_active=True,
                )
                db.add(u)
                db.commit()
                db.refresh(u)

                b = Budget(user_id=u.id, monthly_limit=Decimal(str(random.choice([150, 200, 250, 300, 500]))))
                db.add(b)
                created_users.append(u)
            else:
                created_users.append(existing_u)

        db.commit()

        # 4. Generate Synthetic Subscriptions
        current_sub_count = db.query(Subscription).count()
        target_records = max(num_records, 1000)
        remaining = target_records - current_sub_count

        if remaining > 0:
            print(f"Generating {remaining} additional subscription records across {len(created_users)} users...")
            new_subs = []
            new_expenses = []

            for _ in range(remaining):
                usr = random.choice(created_users)
                template = random.choice(REALISTIC_CATALOG)
                cat_id = categories_dict.get(template["cat"], list(categories_dict.values())[0])

                # Randomize renewal date between past 60 days to next 180 days
                days_offset = random.randint(-45, 120)
                ren_date = today + timedelta(days=days_offset)
                status = SubscriptionStatus.ACTIVE
                if days_offset < 0:
                    status = random.choice([SubscriptionStatus.EXPIRED, SubscriptionStatus.CANCELLED, SubscriptionStatus.ACTIVE])

                # Slight price variation
                base_cost = template["cost"] * random.uniform(0.9, 1.1)

                sub = Subscription(
                    user_id=usr.id,
                    category_id=cat_id,
                    name=f"{template['name']} #{random.randint(100, 999)}" if random.random() < 0.3 else template["name"],
                    cost=Decimal(f"{base_cost:.2f}"),
                    currency="USD",
                    billing_cycle=template["cycle"],
                    start_date=today - timedelta(days=random.randint(90, 720)),
                    renewal_date=ren_date,
                    status=status,
                    auto_renew=(status == SubscriptionStatus.ACTIVE),
                    payment_method=random.choice(PAYMENT_METHODS),
                    utility_score=template["util"],
                    is_essential=template["ess"],
                    description=f"Generated synthetic {template['name']} record.",
                )
                new_subs.append(sub)

            db.bulk_save_objects(new_subs)
            db.commit()

            # Generate associated historical expenses for active subscriptions
            total_after = db.query(Subscription).count()
            print(f"Total subscriptions in database: {total_after}")

            # Add sample expense records for trend analysis
            all_active = db.query(Subscription).filter(Subscription.status == SubscriptionStatus.ACTIVE).limit(200).all()
            for s in all_active:
                for past_month in range(1, 6):
                    exp_date = today - timedelta(days=past_month * 30)
                    new_expenses.append(
                        Expense(
                            user_id=s.user_id,
                            subscription_id=s.id,
                            category_id=s.category_id,
                            amount=s.cost,
                            currency=s.currency,
                            expense_date=exp_date,
                            payment_status=PaymentStatus.PAID,
                            notes=f"Auto-renewal payment for {s.name}",
                        )
                    )
            db.bulk_save_objects(new_expenses)
            db.commit()

        print("Synthetic dataset successfully populated!")
        print(f"Users: {db.query(User).count()}")
        print(f"Subscriptions: {db.query(Subscription).count()}")
        print(f"Expenses: {db.query(Expense).count()}")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    generate_seed_data(1050)
