import os
from core.message_schema import Message
from core.message_broker import MessageBroker


class Processor:
    """
    Handles message validation, enrichment, and routing.
    """

    def __init__(self, outputs, broker: MessageBroker):
        """
        Initialize the Processor with configured outputs and broker.
        :param outputs: List of output configurations from config.yaml
        :param broker: Instance of the MessageBroker for publishing messages
        """
        self.outputs = outputs
        self.broker = broker

    def validate_message(self, message_data: dict) -> Message:
        """
        Validates and parses an incoming message.
        :param message_data: Raw message data
        :return: Parsed and validated Message object
        :raises: ValueError if the message is invalid
        """
        try:
            return Message(**message_data)
        except Exception as e:
            raise ValueError(f"Invalid message format: {e}")

    def enrich_message(self, message: Message) -> Message:
        """
        Adds metadata or enriches the message as needed.
        :param message: Validated Message object
        :return: Enriched Message object
        """
        # Add an enrichment example: attach processing metadata
        message.metadata["processed_by"] = os.getenv("PROCESSOR_NAME", "NotifyStack Processor")
        message.metadata["timestamp_processed"] = message.timestamp
        return message

    def route_message(self, message: Message):
        """
        Routes the message to the appropriate outputs based on configuration.
        :param message: Enriched Message object
        """
        for output in self.outputs:
            if output["type"] == "webhook":
                self.route_to_webhook(output, message)
            elif output["type"] == "twilio":
                self.route_to_twilio(output, message)

    def route_to_webhook(self, config: dict, message: Message):
        """
        Publishes the message to the webhook queue.
        :param config: Webhook configuration
        :param message: Enriched Message object
        """
        queue_name = "webhook_notifications"
        print(f"Routing message to webhook queue: {queue_name}")
        self.broker.publish(queue=queue_name, message=message.dict())

    def route_to_twilio(self, config: dict, message: Message):
        """
        Publishes the message to the Twilio queue.
        :param config: Twilio configuration
        :param message: Enriched Message object
        """
        queue_name = "twilio_notifications"
        print(f"Routing message to Twilio queue: {queue_name}")
        self.broker.publish(queue=queue_name, message=message.dict())

    def process(self, raw_message: dict):
        """
        Main entry point for processing a raw message.
        :param raw_message: Incoming message data
        """
        try:
            # Step 1: Validate the incoming message
            message = self.validate_message(raw_message)

            # Step 2: Enrich the message
            enriched_message = self.enrich_message(message)

            # Step 3: Route the message to appropriate outputs
            self.route_message(enriched_message)

        except ValueError as e:
            print(f"Message validation failed: {e}")
        except Exception as e:
            print(f"Unexpected error during processing: {e}")
