import pytest
from datetime import datetime, timedelta, UTC
from api.db.sql_service.services.subscription_service import SubscriptionService
from api.db.sql_service.models.models import Subscription, PaymentMethod


class TestSubscriptionService:
    """Test cases for SubscriptionService."""

    def test_create_subscription(self, db_session, test_user):
        """Test creating a new subscription."""
        included_functions = ["chat", "file_upload", "api_access"]
        
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="pro",
            included_functions=included_functions,
            price=29.99,
            billing_frequency="monthly",
            user_id=test_user.id
        )
        
        assert subscription is not None
        assert subscription.tier == "pro"
        assert subscription.included_functions == included_functions
        assert subscription.price == 29.99
        assert subscription.billing_frequency == "monthly"
        assert subscription.user_id == test_user.id
        assert subscription.status == "active"
        assert datetime.fromtimestamp(subscription.valid_until_date.timestamp(), UTC) > datetime.now(UTC)

    def test_create_tenant_subscription(self, db_session, test_tenant):
        """Test creating a subscription for a tenant."""
        included_functions = ["team_chat", "file_sharing", "admin_dashboard"]
        
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="enterprise",
            included_functions=included_functions,
            price=99.99,
            billing_frequency="yearly",
            tenant_id=test_tenant.id
        )
        
        assert subscription is not None
        assert subscription.tier == "enterprise"
        assert subscription.tenant_id == test_tenant.id
        assert subscription.billing_frequency == "yearly"
        assert datetime.fromtimestamp(subscription.valid_until_date.timestamp(), UTC) > datetime.now(UTC) + timedelta(days=364)

    def test_add_payment_method(self, db_session, test_user):
        """Test adding a payment method to a subscription."""
        # First create a subscription
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="pro",
            included_functions=["chat"],
            price=29.99,
            billing_frequency="monthly",
            user_id=test_user.id
        )
        
        # Add payment method
        payment_method = SubscriptionService.add_payment_method(
            session=db_session,
            subscription_id=subscription.id,
            method="credit_card",
            card_number="4111111111111111",
            card_holder_name="Test User",
            expiry_date="12/25",
            security_code="123",
            billing_address="123 Test St",
            billing_state="CA",
            billing_country="USA",
            billing_postal_code="12345"
        )
        
        assert payment_method is not None
        assert payment_method.subscription_id == subscription.id
        assert payment_method.method == "credit_card"
        assert payment_method.card_number == "1111"  # Only last 4 digits are stored
        assert payment_method.card_holder_name == "Test User"
        assert payment_method.expiry_date == "12/25"
        assert payment_method.billing_address == "123 Test St"

    def test_get_subscription_by_id(self, db_session, test_user):
        """Test retrieving a subscription by ID."""
        # Create a subscription
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="pro",
            included_functions=["chat"],
            price=29.99,
            billing_frequency="monthly",
            user_id=test_user.id
        )
        
        # Retrieve it by ID
        retrieved = SubscriptionService.get_subscription_by_id(
            session=db_session,
            subscription_id=subscription.id
        )
        
        assert retrieved is not None
        assert retrieved.id == subscription.id
        assert retrieved.tier == "pro"
        assert retrieved.user_id == test_user.id

    def test_get_subscription_by_user(self, db_session, test_user):
        """Test retrieving a user's subscription."""
        # Create a subscription
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="pro",
            included_functions=["chat"],
            price=29.99,
            billing_frequency="monthly",
            user_id=test_user.id
        )
        
        # Retrieve it by user ID
        retrieved = SubscriptionService.get_subscription_by_user(
            session=db_session,
            user_id=test_user.id
        )
        
        assert retrieved is not None
        assert retrieved.id == subscription.id
        assert retrieved.tier == "pro"
        assert retrieved.user_id == test_user.id

    def test_get_subscription_by_tenant(self, db_session, test_tenant):
        """Test retrieving a tenant's subscription."""
        # Create a subscription
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="enterprise",
            included_functions=["team_chat"],
            price=99.99,
            billing_frequency="yearly",
            tenant_id=test_tenant.id
        )
        
        # Retrieve it by tenant ID
        retrieved = SubscriptionService.get_subscription_by_tenant(
            session=db_session,
            tenant_id=test_tenant.id
        )
        
        assert retrieved is not None
        assert retrieved.id == subscription.id
        assert retrieved.tier == "enterprise"
        assert retrieved.tenant_id == test_tenant.id

    def test_cancel_subscription(self, db_session, test_user):
        """Test canceling a subscription."""
        # Create a subscription
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="pro",
            included_functions=["chat"],
            price=29.99,
            billing_frequency="monthly",
            user_id=test_user.id
        )
        
        # Cancel it
        cancelled = SubscriptionService.cancel_subscription(
            session=db_session,
            subscription_id=subscription.id
        )
        
        assert cancelled is not None
        assert cancelled.id == subscription.id
        assert cancelled.status == "cancelled"

    def test_renew_subscription(self, db_session, test_user):
        """Test renewing a subscription."""
        # Create a subscription
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="pro",
            included_functions=["chat"],
            price=29.99,
            billing_frequency="monthly",
            user_id=test_user.id
        )
        
        # Store the original valid_until_date
        original_valid_until = subscription.valid_until_date
        
        # Wait a moment to ensure the new date will be different
        import time
        time.sleep(1)
        
        # Renew it
        renewed = SubscriptionService.renew_subscription(
            session=db_session,
            subscription_id=subscription.id
        )
        
        assert renewed is not None
        assert renewed.id == subscription.id
        assert renewed.status == "active"
        assert datetime.fromtimestamp(renewed.valid_until_date.timestamp(), UTC) > datetime.fromtimestamp(original_valid_until.timestamp(), UTC)

    def test_update_payment_method(self, db_session, test_user):
        """Test updating payment method details."""
        # Create a subscription and payment method
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="pro",
            included_functions=["chat"],
            price=29.99,
            billing_frequency="monthly",
            user_id=test_user.id
        )
        
        payment_method = SubscriptionService.add_payment_method(
            session=db_session,
            subscription_id=subscription.id,
            method="credit_card",
            card_number="4111111111111111",
            card_holder_name="Test User",
            expiry_date="12/25",
            security_code="123",
            billing_address="123 Test St",
            billing_state="CA",
            billing_country="USA",
            billing_postal_code="12345"
        )
        
        # Update payment method
        updated = SubscriptionService.update_payment_method(
            session=db_session,
            subscription_id=subscription.id,
            card_holder_name="Updated User",
            billing_address="456 New St"
        )
        
        assert updated is not None
        assert updated.id == payment_method.id
        assert updated.card_holder_name == "Updated User"
        assert updated.billing_address == "456 New St"
        assert updated.card_number == "1111"  # Should not change

    def test_get_payment_method(self, db_session, test_user):
        """Test retrieving payment method details."""
        # Create a subscription and payment method
        subscription = SubscriptionService.create_subscription(
            session=db_session,
            tier="pro",
            included_functions=["chat"],
            price=29.99,
            billing_frequency="monthly",
            user_id=test_user.id
        )
        
        payment_method = SubscriptionService.add_payment_method(
            session=db_session,
            subscription_id=subscription.id,
            method="credit_card",
            card_number="4111111111111111",
            card_holder_name="Test User",
            expiry_date="12/25",
            security_code="123",
            billing_address="123 Test St",
            billing_state="CA",
            billing_country="USA",
            billing_postal_code="12345"
        )
        
        # Retrieve payment method
        retrieved = SubscriptionService.get_payment_method(
            session=db_session,
            subscription_id=subscription.id
        )
        
        assert retrieved is not None
        assert retrieved.id == payment_method.id
        assert retrieved.method == "credit_card"
        assert retrieved.card_number == "1111"  # Only last 4 digits are stored
        assert retrieved.card_holder_name == "Test User" 