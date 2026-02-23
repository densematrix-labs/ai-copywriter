from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


def generate_token():
    return f"tok_{uuid.uuid4().hex}"


class GenerationToken(Base):
    __tablename__ = "generation_tokens"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    token = Column(String(255), unique=True, nullable=False, default=generate_token)
    product_sku = Column(String(50), nullable=False)
    total_generations = Column(Integer, nullable=False)
    remaining_generations = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    device_id = Column(String(255), index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    token_id = Column(String(36), ForeignKey("generation_tokens.id"), nullable=False)
    product_sku = Column(String(50), nullable=False)
    provider = Column(String(20), nullable=False, default="creem")
    provider_transaction_id = Column(String(255), unique=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(20), nullable=False)
    device_id = Column(String(255))
    optional_email = Column(String(255))
    created_at = Column(DateTime, default=func.now())


class FreeTrialUsage(Base):
    __tablename__ = "free_trial_usage"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(255), unique=True, nullable=False, index=True)
    generations_used = Column(Integer, default=0)
    last_used_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
