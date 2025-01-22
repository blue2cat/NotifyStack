from enum import Enum

class MessageType(Enum):
    """Enum for the different types of messages."""
    INPUT = "input"
    OUTPUT = "output"

class MessageReceiver(Enum):
    """Enum for the different types of receivers."""
    # input
    EMAIL = "email"

    # processing 
    PROCESSOR = "processor"

    # output
    WEBHOOK = "webhook"
