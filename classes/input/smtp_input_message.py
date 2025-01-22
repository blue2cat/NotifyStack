from typing import Dict, List, Optional
from pydantic import Field, EmailStr
from core.message import BaseMessage


class SMTPInputMessage(BaseMessage):
    """
    Schema for incoming SMTP messages to be published to the processing queue.

    Attributes:
    - sender: The sender's email address.
    - recipient: The recipient's email address.
    - subject: The subject of the email.
    - body: The body of the email.
    - metadata: Additional metadata for the message (e.g., headers).
    - attachments: List of file paths representing attachments.
    """
    sender: EmailStr
    recipient: List[EmailStr]
    subject: str
    body: str
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict)
    attachments: Optional[List[str]] = Field(default_factory=list)

    def validate_attachments(self, max_size_mb: int = 10):
        """Validate the size and existence of attachments."""
        import os
        for file_path in self.attachments:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Attachment not found: {file_path}")
            if os.path.getsize(file_path) > max_size_mb * 1024 * 1024:
                raise ValueError(f"Attachment {file_path} exceeds the maximum size of {max_size_mb}MB")
