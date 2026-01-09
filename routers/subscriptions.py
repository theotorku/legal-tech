"""
Subscription management API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from dependencies import get_auth_service, get_subscription_service
from logger import get_logger
from models.subscription_models import (
    CurrentUsage,
    PlanName,
    SubscriptionCreate,
    SubscriptionPlan,
    SubscriptionPlanPublic,
    SubscriptionWithPlan,
    User,
)
from services.auth_service import AuthService
from services.subscription_service import SubscriptionService

logger = get_logger(__name__)
router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
security = HTTPBearer()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Dependency to get current user from JWT token."""
    try:
        token = credentials.credentials
        return await auth_service.verify_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@router.get(
    "/plans",
    response_model=List[SubscriptionPlanPublic],
    summary="Get all subscription plans",
    description="Retrieve all available subscription plans with pricing"
)
async def get_plans(
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Get all available subscription plans.

    Args:
        subscription_service: Subscription service

    Returns:
        List of subscription plans
    """
    try:
        plans = await subscription_service.get_all_plans()
        
        # Convert to public format
        public_plans = []
        for plan in plans:
            savings = (plan.price_monthly * 12) - plan.price_annual
            public_plans.append(
                SubscriptionPlanPublic(
                    **plan.dict(),
                    savings_annual=savings
                )
            )
        
        return public_plans
    
    except Exception as e:
        logger.error(f"Failed to get plans: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plans"
        )


@router.post(
    "/subscribe",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create subscription",
    description="Subscribe to a plan (starts with 14-day free trial)"
)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user_from_token),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Create a new subscription for the current user.

    Args:
        subscription_data: Subscription creation data
        current_user: Current authenticated user
        subscription_service: Subscription service

    Returns:
        Created subscription
    """
    try:
        subscription = await subscription_service.create_subscription(
            current_user.id,
            subscription_data
        )
        
        return {
            "subscription": subscription,
            "message": "Subscription created successfully. Your 14-day free trial has started!"
        }
    
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/my-subscription",
    response_model=SubscriptionWithPlan,
    summary="Get my subscription",
    description="Get the current user's active subscription"
)
async def get_my_subscription(
    current_user: User = Depends(get_current_user_from_token),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Get current user's subscription.

    Args:
        current_user: Current authenticated user
        subscription_service: Subscription service

    Returns:
        User's subscription with plan details
    """
    try:
        subscription = await subscription_service.get_user_subscription(current_user.id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        return subscription
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get subscription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription"
        )


@router.get(
    "/usage",
    response_model=CurrentUsage,
    summary="Get current usage",
    description="Get usage statistics for the current billing period"
)
async def get_usage(
    current_user: User = Depends(get_current_user_from_token),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Get current usage statistics.

    Args:
        current_user: Current authenticated user
        subscription_service: Subscription service

    Returns:
        Current usage statistics
    """
    try:
        usage = await subscription_service.get_current_usage(current_user.id)
        
        if not usage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No usage data found"
            )
        
        return usage
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get usage: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage"
        )


@router.post(
    "/upgrade",
    response_model=dict,
    summary="Upgrade subscription",
    description="Upgrade to a higher-tier plan"
)
async def upgrade_subscription(
    new_plan: PlanName,
    current_user: User = Depends(get_current_user_from_token),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Upgrade subscription to a new plan.

    Args:
        new_plan: New plan name
        current_user: Current authenticated user
        subscription_service: Subscription service

    Returns:
        Updated subscription
    """
    try:
        subscription = await subscription_service.upgrade_subscription(
            current_user.id,
            new_plan
        )
        
        return {
            "subscription": subscription,
            "message": f"Successfully upgraded to {new_plan.value} plan"
        }
    
    except Exception as e:
        logger.error(f"Failed to upgrade subscription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/cancel",
    response_model=dict,
    summary="Cancel subscription",
    description="Cancel the current subscription (effective at end of billing period)"
)
async def cancel_subscription(
    current_user: User = Depends(get_current_user_from_token),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Cancel current subscription.

    Args:
        current_user: Current authenticated user
        subscription_service: Subscription service

    Returns:
        Canceled subscription
    """
    try:
        subscription = await subscription_service.cancel_subscription(current_user.id)
        
        return {
            "subscription": subscription,
            "message": "Subscription canceled. Access will continue until the end of your billing period."
        }
    
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

