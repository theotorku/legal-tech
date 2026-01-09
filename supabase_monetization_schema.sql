-- Monetization Schema for Contract Analyzer API
-- This extends the existing schema with subscription and usage tracking

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);

-- ============================================================================
-- SUBSCRIPTION PLANS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL, -- starter, professional, business, enterprise
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10, 2) NOT NULL,
    price_annual DECIMAL(10, 2) NOT NULL,
    contracts_per_month INTEGER NOT NULL,
    api_rate_limit INTEGER NOT NULL, -- requests per minute
    team_members INTEGER DEFAULT 1,
    data_retention_days INTEGER DEFAULT 30,
    features JSONB DEFAULT '{}', -- feature flags
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default plans
INSERT INTO subscription_plans (name, display_name, description, price_monthly, price_annual, contracts_per_month, api_rate_limit, team_members, data_retention_days, features) VALUES
('starter', 'Starter', 'Perfect for solo practitioners and freelancers', 99.00, 990.00, 50, 5, 1, 30, '{"email_support": true, "basic_analytics": true}'),
('professional', 'Professional', 'Ideal for small law firms and growing companies', 299.00, 2990.00, 200, 20, 5, 90, '{"priority_support": true, "advanced_analytics": true, "webhooks": true, "custom_templates": true}'),
('business', 'Business', 'For mid-size firms and corporate legal departments', 799.00, 7990.00, 1000, 100, 999, 365, '{"phone_support": true, "sso": true, "custom_integrations": true, "dedicated_manager": true, "sla_99_5": true}'),
('enterprise', 'Enterprise', 'Custom solutions for large organizations', 2500.00, 25000.00, 999999, 1000, 999, 999999, '{"24_7_support": true, "custom_ai_training": true, "white_label": true, "on_premise": true, "sla_99_9": true}');

-- ============================================================================
-- SUBSCRIPTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    status VARCHAR(50) NOT NULL, -- trial, active, past_due, canceled, expired
    billing_cycle VARCHAR(20) NOT NULL, -- monthly, annual
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    trial_end TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);

-- ============================================================================
-- USAGE TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    contract_analysis_id UUID REFERENCES contract_analyses(id) ON DELETE SET NULL,
    usage_type VARCHAR(50) NOT NULL, -- contract_analysis, api_call, storage
    quantity INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    billing_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    billing_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast aggregation
CREATE INDEX idx_usage_user_period ON usage_tracking(user_id, billing_period_start, billing_period_end);
CREATE INDEX idx_usage_subscription ON usage_tracking(subscription_id);
CREATE INDEX idx_usage_type ON usage_tracking(usage_type);

-- ============================================================================
-- INVOICES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    stripe_invoice_id VARCHAR(255) UNIQUE,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    amount_due DECIMAL(10, 2) NOT NULL,
    amount_paid DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL, -- draft, open, paid, void, uncollectible
    billing_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    billing_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    due_date TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    invoice_pdf_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_invoices_user_id ON invoices(user_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_stripe_id ON invoices(stripe_invoice_id);

-- ============================================================================
-- OVERAGE CHARGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS overage_charges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    billing_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    billing_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    contracts_included INTEGER NOT NULL,
    contracts_used INTEGER NOT NULL,
    overage_quantity INTEGER NOT NULL,
    price_per_unit DECIMAL(10, 2) NOT NULL,
    total_charge DECIMAL(10, 2) NOT NULL,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_overage_user_period ON overage_charges(user_id, billing_period_start);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscription_plans_updated_at BEFORE UPDATE ON subscription_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE overage_charges ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY users_select_own ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY subscriptions_select_own ON subscriptions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY usage_select_own ON usage_tracking FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY invoices_select_own ON invoices FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY overages_select_own ON overage_charges FOR SELECT USING (auth.uid() = user_id);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get current usage for a user in current billing period
CREATE OR REPLACE FUNCTION get_current_usage(p_user_id UUID)
RETURNS TABLE (
    contracts_used INTEGER,
    contracts_limit INTEGER,
    overage INTEGER,
    billing_period_start TIMESTAMP WITH TIME ZONE,
    billing_period_end TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(ut.id)::INTEGER as contracts_used,
        sp.contracts_per_month as contracts_limit,
        GREATEST(COUNT(ut.id)::INTEGER - sp.contracts_per_month, 0) as overage,
        s.current_period_start,
        s.current_period_end
    FROM subscriptions s
    JOIN subscription_plans sp ON s.plan_id = sp.id
    LEFT JOIN usage_tracking ut ON ut.user_id = s.user_id 
        AND ut.created_at >= s.current_period_start 
        AND ut.created_at < s.current_period_end
        AND ut.usage_type = 'contract_analysis'
    WHERE s.user_id = p_user_id 
        AND s.status IN ('trial', 'active')
    GROUP BY sp.contracts_per_month, s.current_period_start, s.current_period_end;
END;
$$ LANGUAGE plpgsql;

-- Function to check if user has reached their limit
CREATE OR REPLACE FUNCTION check_usage_limit(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_usage_info RECORD;
BEGIN
    SELECT * INTO v_usage_info FROM get_current_usage(p_user_id);
    
    IF v_usage_info IS NULL THEN
        RETURN FALSE; -- No active subscription
    END IF;
    
    -- Allow overage (will be charged)
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

