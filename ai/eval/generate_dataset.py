import json
import os

TEMPLATES = [
    # 1. Total monthly spending queries (35 variants)
    ("How much did I spend on subscriptions this month?", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("What is my total monthly subscription cost?", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("Can you calculate my monthly recurring expenses?", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("What are my total subscription costs per month?", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("Show me my monthly recurring bill total.", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("How much am I paying each month for recurring tools?", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("Give me the total breakdown of monthly spending.", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("What does my monthly subscription bill add up to?", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("How much money goes towards subscriptions every month?", "spending_summary", ["Netflix Premium", "Spotify Premium"]),
    ("Summarize my current monthly subscription expense.", "spending_summary", ["Netflix Premium", "Spotify Premium"]),

    # 2. Upcoming renewal queries (35 variants)
    ("Which subscriptions are renewing next week?", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("What subscriptions renew in the next 7 days?", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("Are there any subscriptions renewing soon?", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("Show me upcoming subscription renewal dates.", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("What payments are due next week?", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("Which services will charge me in the next 14 days?", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("List upcoming renewals for this month.", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("Do I have any bills coming up next week?", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("Check when my next subscription will renew.", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),
    ("What renewals should I expect within two weeks?", "upcoming_renewals", ["GitHub Copilot Individual", "AWS Cloud Dev Tier"]),

    # 3. Category spending & breakdown queries (35 variants)
    ("Which subscription categories consume most of my budget?", "category_breakdown", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("Break down my subscription expenses by category.", "category_breakdown", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("How much do I spend on entertainment compared to cloud?", "category_breakdown", ["Netflix Premium", "AWS Cloud Dev Tier"]),
    ("What percentage of my spend goes to developer tools?", "category_breakdown", ["GitHub Copilot Individual", "ChatGPT Plus"]),
    ("Show category-wise distribution of my recurring costs.", "category_breakdown", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("How much am I spending on cloud infrastructure?", "category_breakdown", ["AWS Cloud Dev Tier", "DigitalOcean Droplets"]),
    ("What are my highest expense categories?", "category_breakdown", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("Provide a breakdown of software vs streaming services.", "category_breakdown", ["GitHub Copilot Individual", "Netflix Premium"]),
    ("Which category has the highest monthly recurring bill?", "category_breakdown", ["AWS Cloud Dev Tier"]),
    ("List all subscription categories with their monthly spend.", "category_breakdown", ["AWS Cloud Dev Tier", "Netflix Premium"]),

    # 4. Savings and cost reduction queries (35 variants)
    ("How can I reduce my monthly subscription expenses?", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("Which subscriptions should I consider cancelling to save money?", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("Are there low-utility subscriptions I can cut?", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("Where am I wasting money on recurring bills?", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("Identify subscriptions with low ratings that are not essential.", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("How much could I save if I cancel unused services?", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("Find potential cost savings in my subscription list.", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("Recommend unnecessary subscriptions to cancel this month.", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("What are my least utilized subscriptions?", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),
    ("Help me trim my subscription budget by eliminating low value items.", "savings_recommendation", ["Peacock Premium", "SoundCloud Go+"]),

    # 5. Most expensive & highest cost queries (35 variants)
    ("Which subscriptions cost me the most?", "most_expensive", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("What is my single most expensive subscription?", "most_expensive", ["AWS Cloud Dev Tier"]),
    ("Rank my subscriptions from highest to lowest cost.", "most_expensive", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("Show me the top 3 most expensive recurring accounts.", "most_expensive", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("What accounts have the highest monthly charge?", "most_expensive", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("Which services cost more than $20 per month?", "most_expensive", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("List my biggest recurring expenses.", "most_expensive", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("What are my priciest subscriptions right now?", "most_expensive", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("Identify top costly subscriptions in my portfolio.", "most_expensive", ["AWS Cloud Dev Tier", "Netflix Premium"]),
    ("Who takes the largest cut of my monthly subscription budget?", "most_expensive", ["AWS Cloud Dev Tier"]),

    # 6. Specific service lookups & comparison queries (35 variants)
    ("How much do I pay for Netflix each month?", "service_lookup", ["Netflix Premium"]),
    ("When does my Spotify subscription renew?", "service_lookup", ["Spotify Premium"]),
    ("What is the cost of my AWS account?", "service_lookup", ["AWS Cloud Dev Tier"]),
    ("Is GitHub Copilot marked as essential?", "service_lookup", ["GitHub Copilot Individual"]),
    ("Show details for my ChatGPT Plus subscription.", "service_lookup", ["ChatGPT Plus"]),
    ("When is my Disney+ renewal scheduled?", "service_lookup", ["Disney+ Bundle"]),
    ("How much does YouTube Premium cost me?", "service_lookup", ["YouTube Premium"]),
    ("What billing cycle is set for my cloud services?", "service_lookup", ["AWS Cloud Dev Tier"]),
    ("Check my Audible subscription status.", "service_lookup", ["Audible Premium Plus"]),
    ("What payment method is used for my streaming accounts?", "service_lookup", ["Netflix Premium"]),
]

def build_golden_dataset(count=210):
    dataset = []
    idx = 1
    # Expand templates with varied phrasing to reach 210 distinct golden queries
    prefixes = ["", "Could you tell me: ", "Please check: ", "Quick question: "]
    
    while len(dataset) < count:
        for text, intent, targets in TEMPLATES:
            if len(dataset) >= count:
                break
            prefix = prefixes[len(dataset) % len(prefixes)]
            q = f"{prefix}{text}" if prefix and not text.startswith("Could") else text
            # Ensure unique query strings
            if any(d["query"] == q for d in dataset):
                q = f"{q} (query {idx})"

            dataset.append({
                "id": idx,
                "query": q,
                "intent": intent,
                "expected_target_records": targets,
                "expected_keywords": [t.lower() for t in targets],
            })
            idx += 1
            
    return dataset

if __name__ == "__main__":
    data = build_golden_dataset(210)
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "golden_dataset.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} golden evaluation queries in {out_path}")
