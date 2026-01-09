"""
Subscription management service.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from supabase import Client

from config import get_settings
from exceptions import ValidationError, NotFoundError
from logger import get_logger
from models.subscription_models import (
    BillingCycle,
    CurrentUsage,
    PlanName,
    Subscription,
    SubscriptionCreate,
    SubscriptionPlan,
    SubscriptionStatus,
    SubscriptionWithPlan,
    UsageRecord,
    UsageType,
)

logger = get_logger(__name__)
settings = get_settings()


class SubscriptionService:
    """Service for managing subscriptions and usage."""

    def __init__(self, db_client: Client):
        """
        Initialize subscription service.

        Args:
            db_client: Supabase client instance
        """
        self.db = db_client

    async def get_all_plans(self) -> List[SubscriptionPlan]:
        """
        Get all active subscription plans.

        Returns:
            List of subscription plans
        """
        try:
            result = self.db.table("subscription_plans").select("*").eq(
                "is_active", True
            ).order("price_monthly").execute()

            plans = [SubscriptionPlan(**plan) for plan in result.data]
            logger.info(f"Retrieved {len(plans)} subscription plans")
            return plans

        except Exception as e:
            logger.error(f"Failed to get subscription plans: {str(e)}", exc_info=True)
            raise

    async def get_plan_by_name(self, plan_name: PlanName) -> SubscriptionPlan:
        """
        Get subscription plan by name.

        Args:
            plan_name: Plan name

        Returns:
            Subscription plan

        Raises:
            NotFoundError: If plan not found
        """
        try:
            result = self.db.table("subscription_plans").select("*").eq(
                "name", plan_name.value
            ).eq("is_active", True).execute()

            if not result.data:
                raise NotFoundError(f"Plan '{plan_name}' not found")

            return SubscriptionPlan(**result.data[0])

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get plan: {str(e)}", exc_info=True)
            raise

    async def create_subscription(
        self,
        user_id: UUID,
        subscription_data: SubscriptionCreate
    ) -> Subscription:
        """
        Create a new subscription for a user.

        Args:
            user_id: User ID
            subscription_data: Subscription creation data

        Returns:
            Created subscription

        Raises:
            ValidationError: If user already has active subscription
        """
        try:
            # Check if user already has an active subscription
            existing = self.db.table("subscriptions").select("id").eq(
                "user_id", str(user_id)
            ).in_("status", ["trial", "active"]).execute()

            if existing.data:
                raise ValidationError("User already has an active subscription")

            # Get plan
            plan = await self.get_plan_by_name(subscription_data.plan_name)

            # Calculate period dates
            now = datetime.utcnow()
            trial_end = now + timedelta(days=14)  # 14-day trial
            period_end = trial_end

            # Create subscription
            sub_dict = {
                "user_id": str(user_id),
                "plan_id": str(plan.id),
                "status": SubscriptionStatus.TRIAL.value,
                "billing_cycle": subscription_data.billing_cycle.value,
                "current_period_start": now.isoformat(),
                "current_period_end": period_end.isoformat(),
                "trial_end": trial_end.isoformat(),
            }

            result = self.db.table("subscriptions").insert(sub_dict).execute()
            if not result.data:
                raise ValidationError("Failed to create subscription")

            subscription = Subscription(**result.data[0])
            logger.info(
                f"Subscription created for user {user_id}: "
                f"{subscription_data.plan_name} ({subscription_data.billing_cycle})"
            )
            return subscription

        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to create subscription: {str(e)}", exc_info=True)
            raise

    async def get_user_subscription(self, user_id: UUID) -> Optional[SubscriptionWithPlan]:
        """
        Get active subscription for a user with plan details.

        Args:
            user_id: User ID

        Returns:
            Subscription with plan or None if no active subscription
        """
        try:
            result = self.db.table("subscriptions").select(
                "*, plan:subscription_plans(*)"
            ).eq("user_id", str(user_id)).in_(
                "status", ["trial", "active"]
            ).order("created_at", desc=True).limit(1).execute()

            if not result.data:
                return None

            data = result.data[0]
            plan_data = data.pop("plan")
            
            subscription = Subscription(**data)
            plan = SubscriptionPlan(**plan_data)
            
            return SubscriptionWithPlan(**subscription.dict(), plan=plan)

        except Exception as e:
            logger.error(
                f"Failed to get user subscription: {str(e)}", exc_info=True
            )
            raise

    async def track_usage(
        self,
        user_id: UUID,
        usage_type: UsageType,
        quantity: int = 1,
        contract_analysis_id: Optional[UUID] = None,
        metadata: dict = None
    ) -> UsageRecord:
        """
        Track usage for a user.

        Args:
            user_id: User ID
            usage_type: Type of usage
            quantity: Quantity used
            contract_analysis_id: Related contract analysis ID
            metadata: Additional metadata

        Returns:
            Usage record
        """
        try:
            # Get user's subscription
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                raise ValidationError("No active subscription found")

            # Create usage record
            usage_dict = {
                "user_id": str(user_id),
                "subscription_id": str(subscription.id),
                "contract_analysis_id": str(contract_analysis_id) if contract_analysis_id else None,
                "usage_type": usage_type.value,
                "quantity": quantity,
                "metadata": metadata or {},
                "billing_period_start": subscription.current_period_start.isoformat(),
                "billing_period_end": subscription.current_period_end.isoformat(),
            }

            result = self.db.table("usage_tracking").insert(usage_dict).execute()
            if not result.data:
                raise ValidationError("Failed to track usage")

            usage_record = UsageRecord(**result.data[0])
            logger.debug(
                f"Usage tracked for user {user_id}: "
                f"{usage_type.value} x{quantity}"
            )
            return usage_record

        except Exception as e:
            logger.error(f"Failed to track usage: {str(e)}", exc_info=True)
            raise

    async def get_current_usage(self, user_id: UUID) -> Optional[CurrentUsage]:
        """
        Get current usage statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Current usage statistics or None if no subscription
        """
        try:
            # Use database function
            result = self.db.rpc(
                "get_current_usage",
                {"p_user_id": str(user_id)}
            ).execute()

            if not result.data:
                return None

            usage_data = result.data[0]
            return CurrentUsage(**usage_data)

        except Exception as e:
            logger.error(f"Failed to get current usage: {str(e)}", exc_info=True)
            raise

    async def check_usage_limit(self, user_id: UUID) -> bool:
        """
        Check if user can make another API call.

        Args:
            user_id: User ID

        Returns:
            True if user can proceed, False otherwise
        """
        try:
            # Use database function
            result = self.db.rpc(
                "check_usage_limit",
                {"p_user_id": str(user_id)}
            ).execute()

            return result.data if result.data else False

        except Exception as e:
            logger.error(f"Failed to check usage limit: {str(e)}", exc_info=True)
            return False

    async def upgrade_subscription(
        self,
        user_id: UUID,
        new_plan_name: PlanName
    ) -> Subscription:
        """
        Upgrade user's subscription to a new plan.

        Args:
            user_id: User ID
            new_plan_name: New plan name

        Returns:
            Updated subscription

        Raises:
            ValidationError: If upgrade is invalid
        """
        try:
            # Get current subscription
            current_sub = await self.get_user_subscription(user_id)
            if not current_sub:
                raise ValidationError("No active subscription found")

            # Get new plan
            new_plan = await self.get_plan_by_name(new_plan_name)

            # Update subscription
            result = self.db.table("subscriptions").update({
                "plan_id": str(new_plan.id)
            }).eq("id", str(current_sub.id)).execute()

            if not result.data:
                raise ValidationError("Failed to upgrade subscription")

            subscription = Subscription(**result.data[0])
            logger.info(
                f"Subscription upgraded for user {user_id}: "
                f"{current_sub.plan.name} -> {new_plan_name}"
            )
            return subscription

        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to upgrade subscription: {str(e)}", exc_info=True)
            raise

    async def cancel_subscription(self, user_id: UUID) -> Subscription:
        """
        Cancel user's subscription.

        Args:
            user_id: User ID

        Returns:
            Canceled subscription

        Raises:
            ValidationError: If no active subscription
        """
        try:
            # Get current subscription
            current_sub = await self.get_user_subscription(user_id)
            if not current_sub:
                raise ValidationError("No active subscription found")

            # Update subscription
            result = self.db.table("subscriptions").update({
                "status": SubscriptionStatus.CANCELED.value,
                "canceled_at": datetime.utcnow().isoformat()
            }).eq("id", str(current_sub.id)).execute()

            if not result.data:
                raise ValidationError("Failed to cancel subscription")

            subscription = Subscription(**result.data[0])
            logger.info(f"Subscription canceled for user {user_id}")
            return subscription

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}", exc_info=True)
            raise

