import pika
import json
from logger import Logger

class MessageBroker:
    def __init__(self, host: str, port: int, username: str, password: str):
        """
        Initializes the MessageBroker with RabbitMQ connection settings.
        :param host: RabbitMQ server host
        :param port: RabbitMQ server port
        :param username: RabbitMQ username
        :param password: RabbitMQ password
        """
        # Initialize the logger
        self.logger = Logger.get_logger()

        # Establish RabbitMQ connection
        self.logger.info("Connecting to RabbitMQ...")
        self.logger.debug(f"Host: {host}, Port: {port}, Username: {username}")
        
        credentials = pika.PlainCredentials(username, password)
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
            self.channel = self.connection.channel()
            self.logger.info("Connected to RabbitMQ successfully.")
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def publish(self, queue: str, message: dict):
        """
        Publishes a message to a RabbitMQ queue.
        :param queue: Queue name
        :param message: Message dictionary to publish
        """
        try:
            # Declare the queue if it doesn't exist
            self.channel.queue_declare(queue=queue, durable=True)

            # Publish the message to the queue
            self.channel.basic_publish(

                # Set direct exchange
                exchange='',

                # Set routing key to queue name
                routing_key=queue,

                # Set message properties
                body=message.to_json(),

                # Set message as persistent
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )
            
            self.logger.info(f"Message published to queue '{queue}': {message}")
        except Exception as e:
            self.logger.error(f"Failed to publish message to queue '{queue}': {e}")

    def consume(self, queue: str, callback):
        """
        Consumes messages from a RabbitMQ queue.
        :param queue: Queue name
        :param callback: Function to process each message
        """
        try:
            self.channel.queue_declare(queue=queue, durable=True)
            self.logger.debug(f"Message broker is consuming messages from queue '{queue}'.")

            def on_message(channel, method, properties, body):
                message = json.loads(body)
                self.logger.debug(f"Message received from queue '{queue}': {message}")
                callback(message)
                channel.basic_ack(delivery_tag=method.delivery_tag)

            self.channel.basic_consume(queue=queue, on_message_callback=on_message)
            self.logger.info(f"Started consuming messages from queue '{queue}'.")
            self.channel.start_consuming()
        except Exception as e:
            self.logger.error(f"Failed to consume messages from queue '{queue}': {e}")