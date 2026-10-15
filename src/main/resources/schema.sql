-- Schema DDL for Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    billing_frequency VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    next_renewal_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    cancellation_date DATE NULL,
    notes VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sub_renewal_status ON subscriptions (next_renewal_date, status);
CREATE INDEX IF NOT EXISTS idx_sub_category_status ON subscriptions (category, status);
CREATE INDEX IF NOT EXISTS idx_sub_status ON subscriptions (status);
