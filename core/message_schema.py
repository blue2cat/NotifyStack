from pydantic import BaseModel, Field, ValidationError
from typing import Dict
from datetime import datetime
import uuid

class BaseMessage(BaseModel):
    """Base class for all messages"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    timestamp: datetime = Field(default_factory=datetime.now)

class EmailMessage(BaseMessage):
    """"""
    type: str = Field(default="email", const=True)
    payload: Dict[str, str]

    @validator("payload")
    def validate_email_payload(cls, payload):
        required_keys = {"subject", "body", "to", "from"}
        missing_keys = required_keys - payload.keys()
        if missing_keys:
            raise ValueError(f"Payload for 'email' is missing required keys: {missing_keys}")
        return payload

class WebhookMessage(BaseMessage):
    type: str = Field(default="webhook", const=True)
    payload: Dict[str, str]

    @validator("payload")
    def validate_webhook_payload(cls, payload):
        required_keys = {"url", "method"}
        missing_keys = required_keys - payload.keys()
        if missing_keys:
            raise ValueError(f"Payload for 'webhook' is missing required keys: {missing_keys}")
        return payload
