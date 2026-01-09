"""
Pydantic models for subscription and billing management.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class PlanName(str, Enum):
    """Subscription plan names."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    """Billing cycle options."""
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, Enum):
    """Subscription status values."""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class InvoiceStatus(str, Enum):
    """Invoice status values."""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


# ============================================================================
# Subscription Plan Models
# ============================================================================

class SubscriptionPlanFeatures(BaseModel):
    """Features included in a subscription plan."""
    email_support: bool = False
    priority_support: bool = False
    phone_support: bool = False
    support_24_7: bool = False
    basic_analytics: bool = False
    advanced_analytics: bool = False
    webhooks: bool = False
    custom_templates: bool = False
    sso: bool = False
    custom_integrations: bool = False
    dedicated_manager: bool = False
    custom_ai_training: bool = False
    white_label: bool = False
    on_premise: bool = False
    sla_99_5: bool = False
    sla_99_9: bool = False


class SubscriptionPlan(BaseModel):
    """Subscription plan details."""
    id: UUID
    name: PlanName
    display_name: str
    description: Optional[str] = None
    price_monthly: Decimal
    price_annual: Decimal
    contracts_per_month: int
    api_rate_limit: int
    team_members: int
    data_retention_days: int
    features: SubscriptionPlanFeatures
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionPlanPublic(BaseModel):
    """Public-facing subscription plan (for pricing page)."""
    name: PlanName
    display_name: str
    description: Optional[str] = None
    price_monthly: Decimal
    price_annual: Decimal
    contracts_per_month: int
    api_rate_limit: int
    team_members: int
    data_retention_days: int
    features: SubscriptionPlanFeatures
    savings_annual: Decimal = Field(description="Annual savings amount")

    @validator('savings_annual', always=True)
    def calculate_savings(cls, v, values):
        """Calculate annual savings."""
        if 'price_monthly' in values and 'price_annual' in values:
            monthly_total = values['price_monthly'] * 12
            return monthly_total - values['price_annual']
        return Decimal(0)


# ============================================================================
# User Models
# ============================================================================

class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class User(BaseModel):
    """User model."""
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    api_key: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user information."""
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool
    email_verified: bool
    created_at: datetime


# ============================================================================
# Subscription Models
# ============================================================================

class SubscriptionCreate(BaseModel):
    """Create subscription request."""
    plan_name: PlanName
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    payment_method_id: Optional[str] = None  # Stripe payment method ID


class Subscription(BaseModel):
    """Subscription model."""
    id: UUID
    user_id: UUID
    plan_id: UUID
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionWithPlan(Subscription):
    """Subscription with plan details."""
    plan: SubscriptionPlan


class SubscriptionUpdate(BaseModel):
    """Update subscription request."""
    plan_name: Optional[PlanName] = None
    billing_cycle: Optional[BillingCycle] = None


# ============================================================================
# Usage Tracking Models
# ============================================================================

class UsageType(str, Enum):
    """Usage tracking types."""
    CONTRACT_ANALYSIS = "contract_analysis"
    API_CALL = "api_call"
    STORAGE = "storage"


class UsageRecord(BaseModel):
    """Usage tracking record."""
    id: UUID
    user_id: UUID
    subscription_id: Optional[UUID] = None
    contract_analysis_id: Optional[UUID] = None
    usage_type: UsageType
    quantity: int = 1
    metadata: Dict[str, Any] = {}
    billing_period_start: datetime
    billing_period_end: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class CurrentUsage(BaseModel):
    """Current usage statistics for a user."""
    contracts_used: int
    contracts_limit: int
    overage: int
    billing_period_start: datetime
    billing_period_end: datetime
    percentage_used: float

    @validator('percentage_used', always=True)
    def calculate_percentage(cls, v, values):
        """Calculate usage percentage."""
        if 'contracts_used' in values and 'contracts_limit' in values:
            if values['contracts_limit'] > 0:
                return (values['contracts_used'] / values['contracts_limit']) * 100
        return 0.0


# ============================================================================
# Invoice Models
# ============================================================================

class Invoice(BaseModel):
    """Invoice model."""
    id: UUID
    user_id: UUID
    subscription_id: Optional[UUID] = None
    stripe_invoice_id: Optional[str] = None
    invoice_number: str
    amount_due: Decimal
    amount_paid: Decimal
    currency: str = "USD"
    status: InvoiceStatus
    billing_period_start: datetime
    billing_period_end: datetime
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    invoice_pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Overage Models
# ============================================================================

class OverageCharge(BaseModel):
    """Overage charge model."""
    id: UUID
    user_id: UUID
    subscription_id: UUID
    billing_period_start: datetime
    billing_period_end: datetime
    contracts_included: int
    contracts_used: int
    overage_quantity: int
    price_per_unit: Decimal
    total_charge: Decimal
    invoice_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

