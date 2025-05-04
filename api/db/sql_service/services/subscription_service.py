from datetime import datetime, timedelta, UTC
from beartype.typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from api.db.sql_service.models.models import Subscription, PaymentMethod
from api.db.sql_service.services.base import BaseService
from api.utils import get_uuid


class SubscriptionService(BaseService):
    """Service for managing subscriptions and payment methods."""
    model_class = Subscription

    @classmethod
    def create_subscription(
        cls,
        session: Session,
        tier: str,
        included_functions: List[str],
        price: float,
        billing_frequency: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Subscription:
        """Create a new subscription."""
        if not user_id and not tenant_id:
            raise ValueError("Either user_id or tenant_id must be provided")

        start_date = datetime.now(UTC)
        if billing_frequency == "monthly":
            valid_until = start_date + timedelta(days=30)
        else:  # yearly
            valid_until = start_date + timedelta(days=365)

        subscription = cls.save(
            session=session,
            tier=tier,
            included_functions=included_functions,
            price=price,
            start_date=start_date.replace(tzinfo=None),  # Store as naive datetime
            valid_until_date=valid_until.replace(tzinfo=None),  # Store as naive datetime
            billing_frequency=billing_frequency,
            next_billing_date=valid_until.replace(tzinfo=None),  # Store as naive datetime
            status="active",
            user_id=user_id,
            tenant_id=tenant_id,
        )
        return subscription

    @classmethod
    def add_payment_method(
        cls,
        session: Session,
        subscription_id: str,
        method: str,
        card_number: Optional[str] = None,
        card_holder_name: Optional[str] = None,
        expiry_date: Optional[str] = None,
        security_code: Optional[str] = None,
        billing_address: str = None,
        billing_state: str = None,
        billing_country: str = None,
        billing_postal_code: str = None,
    ) -> PaymentMethod:
        """Add a payment method to a subscription."""
        # In a real application, you would encrypt sensitive data
        # and only store the last 4 digits of the card number
        if card_number:
            card_number = card_number[-4:]  # Store only last 4 digits

        payment_method = PaymentMethod(
            id=get_uuid(),
            subscription_id=subscription_id,
            method=method,
            card_number=card_number,
            card_holder_name=card_holder_name,
            expiry_date=expiry_date,
            security_code=security_code,
            billing_address=billing_address,
            billing_state=billing_state,
            billing_country=billing_country,
            billing_postal_code=billing_postal_code,
        )
        session.add(payment_method)
        session.commit()
        return payment_method

    @classmethod
    def get_subscription_by_id(cls, session: Session, subscription_id: str) -> Optional[Subscription]:
        """Get a subscription by ID."""
        return cls.get_by_id(session=session, record_id=subscription_id)

    @classmethod
    def get_subscription_by_user(cls, session: Session, user_id: str) -> Optional[Subscription]:
        """Get a user's subscription."""
        return cls.get(session=session, user_id=user_id)

    @classmethod
    def get_subscription_by_tenant(cls, session: Session, tenant_id: str) -> Optional[Subscription]:
        """Get a tenant's subscription."""
        return cls.get(session=session, tenant_id=tenant_id)

    @classmethod
    def update_subscription_status(
        cls, session: Session, subscription_id: str, status: str
    ) -> Optional[Subscription]:
        """Update a subscription's status."""
        return cls.update_by_id(session=session, record_id=subscription_id, data={"status": status})

    @classmethod
    def cancel_subscription(cls, session: Session, subscription_id: str) -> Optional[Subscription]:
        """Cancel a subscription."""
        return cls.update_subscription_status(session=session, subscription_id=subscription_id, status="cancelled")

    @classmethod
    def renew_subscription(cls, session: Session, subscription_id: str) -> Optional[Subscription]:
        """Renew a subscription."""
        subscription = cls.get_by_id(session=session, record_id=subscription_id)
        if subscription:
            current_date = datetime.now(UTC)
            if subscription.billing_frequency == "monthly":
                new_valid_until = current_date + timedelta(days=30)
            else:  # yearly
                new_valid_until = current_date + timedelta(days=365)

            return cls.update_by_id(
                session=session,
                record_id=subscription_id,
                data={
                    "valid_until_date": new_valid_until.replace(tzinfo=None),  # Store as naive datetime
                    "next_billing_date": new_valid_until.replace(tzinfo=None),  # Store as naive datetime
                    "status": "active"
                }
            )
        return None

    @classmethod
    def get_payment_method(cls, session: Session, subscription_id: str) -> Optional[PaymentMethod]:
        """Get payment method for a subscription."""
        return (
            session.query(PaymentMethod)
            .filter_by(subscription_id=subscription_id)
            .first()
        )

    @classmethod
    def update_payment_method(
        cls,
        session: Session,
        subscription_id: str,
        method: Optional[str] = None,
        card_number: Optional[str] = None,
        card_holder_name: Optional[str] = None,
        expiry_date: Optional[str] = None,
        security_code: Optional[str] = None,
        billing_address: Optional[str] = None,
        billing_state: Optional[str] = None,
        billing_country: Optional[str] = None,
        billing_postal_code: Optional[str] = None,
    ) -> Optional[PaymentMethod]:
        """Update payment method details."""
        payment_method = cls.get_payment_method(session=session, subscription_id=subscription_id)
        if payment_method:
            if method:
                payment_method.method = method
            if card_number:
                payment_method.card_number = card_number[-4:]  # Store only last 4 digits
            if card_holder_name:
                payment_method.card_holder_name = card_holder_name
            if expiry_date:
                payment_method.expiry_date = expiry_date
            if security_code:
                payment_method.security_code = security_code
            if billing_address:
                payment_method.billing_address = billing_address
            if billing_state:
                payment_method.billing_state = billing_state
            if billing_country:
                payment_method.billing_country = billing_country
            if billing_postal_code:
                payment_method.billing_postal_code = billing_postal_code
            session.commit()
        return payment_method 