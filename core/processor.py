import os
from core.message import Message
from core.message_broker import MessageBroker
from classes.message_types import MessageAdapter, MessageType
from classes.input.smtp_input_message import SMTPInputMessage

class Processor:
    """
    Handles message validation, enrichment, and routing.
    """

    def __init__(self, outputs, routes, broker: MessageBroker):
        """
        Initialize the Processor with configured outputs, routes, and broker.
        :param outputs: List of output configurations from config.yaml
        :param routes: List of routing rules from config.yaml
        :param broker: Instance of the MessageBroker for publishing messages
        """
        self.outputs = {output["name"]: output for output in outputs}  # Map outputs by name
        self.routes = routes  # List of routing rules
        self.broker = broker
        self.logger = broker.logger  # Use the broker's logger

    def deserialize_message(self, raw_message: dict) -> Message:
        """
        Deserialize the raw json message data into a Message object.
        :param raw_message: Incoming message data
        :return: Message object
        """
        try:
            # Deserialize the message as a Message object
            message = Message.from_json(raw_message)

            if message.messageType is MessageAdapter.EMAIL and message.messageReceiver is MessageAdapter.PROCESSOR:
                self.logger.debug("Deserializing SMTPInputMessage...")
                message = SMTPInputMessage.from_json(raw_message)
            else:
                self.logger.error(f"Unsupported message type: {message.messageType}")

            return message
        except Exception as e:
            self.logger.error(f"Failed to deserialize message: {e}")
            raise

    def match_routes(self, message: Message) -> list:
        """
        Match the message against routing rules.
        :param message: Message object
        :return: List of output adapter names to route the message to
        """
        matched_routes = []
        for route in self.routes:
            if route["from"] != message.source:
                continue  # Skip routes that don't match the source adapter
            
            conditions = route.get("conditions", {})
            if "metadata" in conditions:
                for key, value in conditions["metadata"].items():
                    if message.metadata.get(key) != value:
                        break
                else:
                    matched_routes.append(route["to"])
            elif "payload_contains" in conditions:
                for key, value in conditions["payload_contains"].items():
                    if message.payload.get(key) != value:
                        break
                else:
                    matched_routes.append(route["to"])
            else:
                matched_routes.append(route["to"])  # No conditions mean always match
        return matched_routes

    def process(self, raw_message: dict):
        """
        Main entry point for processing a raw message.
        :param raw_message: Incoming message data
        """
        try:
            # Step 1: Deserialize the message
            message = self.deserialize_message(raw_message)

            # Step 2: Match the message against routing rules
            destinations = self.match_routes(message)
            if not destinations:
                self.logger.warning(f"No routes matched for message from {message.source}.")
                return

            # Step 3: Publish the message to matched destinations
            for destination in destinations:
                if destination in self.outputs:
                    self.broker.publish(destination, message)
                    self.logger.info(f"Message routed to {destination}: {message.id}")
                else:
                    self.logger.error(f"Output adapter '{destination}' not configured.")

            # Step 4: Publish the message to the database queue
            db_message = message.copy()
            db_message.messageReceiver = MessageAdapter.DATABASE
            self.broker.publish("database", db_message)

        except ValueError as e:
            self.logger.error(f"Invalid message: {e}")
        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")
