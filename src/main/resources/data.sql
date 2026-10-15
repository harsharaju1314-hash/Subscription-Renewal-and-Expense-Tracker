-- Seed Initial Subscription Data for Local Exploration
INSERT INTO subscriptions (name, category, amount, currency, billing_frequency, start_date, next_renewal_date, status, notes, created_at, updated_at)
VALUES
('Netflix Premium', 'STREAMING', 19.99, 'USD', 'MONTHLY', '2026-01-15', '2026-10-20', 'ACTIVE', '4K Ultra HD family plan', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('GitHub Copilot Business', 'SOFTWARE', 19.00, 'USD', 'MONTHLY', '2026-02-01', '2026-10-25', 'ACTIVE', 'AI pair programmer subscription', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Spotify Duo', 'STREAMING', 14.99, 'USD', 'MONTHLY', '2026-03-10', '2026-10-18', 'ACTIVE', 'Music streaming for two accounts', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('JetBrains All Products Pack', 'SOFTWARE', 289.00, 'USD', 'ANNUALLY', '2026-01-20', '2027-01-20', 'ACTIVE', 'Full IDE suite for Java development', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('AWS Cloud Workload', 'CLOUD', 35.50, 'USD', 'MONTHLY', '2026-04-05', '2026-11-05', 'ACTIVE', 'EC2 & RDS demo environment', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Equinox Fitness', 'FITNESS', 65.00, 'USD', 'MONTHLY', '2026-05-01', '2026-11-01', 'ACTIVE', 'Health club and gym membership', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Bloomberg Financial News', 'NEWS', 75.00, 'USD', 'QUARTERLY', '2026-04-15', '2026-10-28', 'ACTIVE', 'Market and technology insights', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Claude Pro Team', 'SOFTWARE', 20.00, 'USD', 'MONTHLY', '2026-06-12', '2026-10-22', 'ACTIVE', 'AI research assistant', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
