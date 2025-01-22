from enum import Enum

class MessageType(Enum):
    """Enum for the different types of messages."""
    INPUT = "input"
    OUTPUT = "output"

class MessageAdapter(Enum):
    """Enum for the different types of receivers."""
    # input
    EMAIL = "email"

    # processing 
    PROCESSOR = "processor"

    # storage
    DATABASE = "database"

    # output
    WEBHOOK = "webhook"
