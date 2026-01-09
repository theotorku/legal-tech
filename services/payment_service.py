"""
Payment processing service using Stripe.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

import stripe
from supabase import Client

from config import get_settings
from exceptions import PaymentError, ValidationError
from logger import get_logger
from models.subscription_models import (
    BillingCycle,
    PlanName,
    SubscriptionStatus,
)

logger = get_logger(__name__)
settings = get_settings()


class PaymentService:
    """Service for handling payments via Stripe."""

    def __init__(self, db_client: Client, stripe_api_key: str):
        """
        Initialize payment service.

        Args:
            db_client: Supabase client instance
            stripe_api_key: Stripe API key
        """
        self.db = db_client
        stripe.api_key = stripe_api_key
        logger.info("Payment service initialized with Stripe")

    async def create_customer(
        self,
        user_id: UUID,
        email: str,
        name: Optional[str] = None
    ) -> str:
        """
        Create a Stripe customer.

        Args:
            user_id: User ID
            email: Customer email
            name: Customer name

        Returns:
            Stripe customer ID

        Raises:
            PaymentError: If customer creation fails
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": str(user_id)}
            )
            logger.info(f"Stripe customer created: {customer.id} for user {user_id}")
            return customer.id

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}", exc_info=True)
            raise PaymentError(f"Failed to create customer: {str(e)}")

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 14
    ) -> dict:
        """
        Create a Stripe subscription.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_days: Trial period in days

        Returns:
            Subscription data

        Raises:
            PaymentError: If subscription creation fails
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days,
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            
            logger.info(
                f"Stripe subscription created: {subscription.id} "
                f"for customer {customer_id}"
            )
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }

        except stripe.error.StripeError as e:
            logger.error(
                f"Failed to create Stripe subscription: {str(e)}", exc_info=True
            )
            raise PaymentError(f"Failed to create subscription: {str(e)}")

    async def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str
    ) -> dict:
        """
        Update a Stripe subscription to a new plan.

        Args:
            subscription_id: Stripe subscription ID
            new_price_id: New Stripe price ID

        Returns:
            Updated subscription data

        Raises:
            PaymentError: If update fails
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id,
                }],
                proration_behavior="create_prorations"
            )
            
            logger.info(f"Stripe subscription updated: {subscription_id}")
            return {
                "subscription_id": updated_subscription.id,
                "status": updated_subscription.status
            }

        except stripe.error.StripeError as e:
            logger.error(
                f"Failed to update Stripe subscription: {str(e)}", exc_info=True
            )
            raise PaymentError(f"Failed to update subscription: {str(e)}")

    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True
    ) -> dict:
        """
        Cancel a Stripe subscription.

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Cancel at end of billing period

        Returns:
            Canceled subscription data

        Raises:
            PaymentError: If cancellation fails
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Stripe subscription canceled: {subscription_id}")
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at
            }

        except stripe.error.StripeError as e:
            logger.error(
                f"Failed to cancel Stripe subscription: {str(e)}", exc_info=True
            )
            raise PaymentError(f"Failed to cancel subscription: {str(e)}")

    async def create_invoice_item(
        self,
        customer_id: str,
        amount: Decimal,
        description: str,
        currency: str = "usd"
    ) -> str:
        """
        Create an invoice item (for overage charges).

        Args:
            customer_id: Stripe customer ID
            amount: Amount in dollars
            description: Item description
            currency: Currency code

        Returns:
            Invoice item ID

        Raises:
            PaymentError: If creation fails
        """
        try:
            # Convert to cents
            amount_cents = int(amount * 100)
            
            invoice_item = stripe.InvoiceItem.create(
                customer=customer_id,
                amount=amount_cents,
                currency=currency,
                description=description
            )
            
            logger.info(
                f"Invoice item created: {invoice_item.id} "
                f"for ${amount} ({description})"
            )
            return invoice_item.id

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create invoice item: {str(e)}", exc_info=True)
            raise PaymentError(f"Failed to create invoice item: {str(e)}")

    async def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        """
        Handle Stripe webhook events.

        Args:
            payload: Webhook payload
            sig_header: Stripe signature header

        Returns:
            Event data

        Raises:
            PaymentError: If webhook verification fails
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            logger.info(f"Stripe webhook received: {event['type']}")
            
            # Handle different event types
            if event["type"] == "customer.subscription.updated":
                await self._handle_subscription_updated(event["data"]["object"])
            elif event["type"] == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event["data"]["object"])
            elif event["type"] == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(event["data"]["object"])
            elif event["type"] == "invoice.payment_failed":
                await self._handle_payment_failed(event["data"]["object"])
            
            return event

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise PaymentError("Invalid webhook signature")
        except Exception as e:
            logger.error(f"Webhook handling failed: {str(e)}", exc_info=True)
            raise

    async def _handle_subscription_updated(self, subscription: dict):
        """Handle subscription updated event."""
        # Update subscription status in database
        logger.info(f"Handling subscription update: {subscription['id']}")
        # Implementation depends on your database schema

    async def _handle_subscription_deleted(self, subscription: dict):
        """Handle subscription deleted event."""
        logger.info(f"Handling subscription deletion: {subscription['id']}")
        # Update subscription status to canceled

    async def _handle_payment_succeeded(self, invoice: dict):
        """Handle successful payment event."""
        logger.info(f"Payment succeeded for invoice: {invoice['id']}")
        # Update invoice status to paid

    async def _handle_payment_failed(self, invoice: dict):
        """Handle failed payment event."""
        logger.warning(f"Payment failed for invoice: {invoice['id']}")
        # Update subscription status to past_due

