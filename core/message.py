from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from classes.message_types import MessageType, MessageReceiver

class BaseMessage(BaseModel):
    """
    Base class for all messages.
    
    Attributes:
    - id: Unique identifier for the message.
    - timestamp: Timestamp of when the message was created.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    messageType: MessageType
    messageReceiver: MessageReceiver

    def __str__(self):
        return f"{self.__class__.__name__} - {self.id}"

    def to_json(self) -> str:
        """Serialize the message to JSON."""
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str):
        """Deserialize a JSON string to a message object."""
        return cls.model_validate_json(json_str)