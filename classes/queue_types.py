# RabbitMQ queue types\
from enum import Enum

class QueueType(Enum):
    """Enum for the different types of RabbitMQ queues."""
    PROCESSING = "processing"
    OUTPUT = "output"

