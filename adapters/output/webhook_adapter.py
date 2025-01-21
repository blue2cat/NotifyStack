import requests
from core.message_schema import Message
from core.message_broker import MessageBroker

class WebhookAdapter:
    def __init__(self, config, broker: MessageBroker):
        self.url = config["url"]
        self.broker = broker

    def send_webhook(self, message: dict):
        """
        Sends the message payload to the configured webhook URL.
        """
        try:
            #response = requests.post(self.url, json=message["payload"])
            print(f"Webhook sent to {self.url}")
        except Exception as e:
            print(f"Failed to send webhook: {e}")

    def start(self):
        """
        Starts listening to the broker for messages and sends them to the webhook.
        """
        self.broker.consume(queue="notifications", callback=self.send_webhook)
