import os
import asyncio
from dotenv import load_dotenv
import yaml
from core.message_broker import MessageBroker
from adapters.input.smtp_adapter import SMTPAdapter
from adapters.output.webhook_adapter import WebhookAdapter


def load_config():
    """
    Loads the YAML configuration and resolves placeholders using environment variables.
    :return: Parsed configuration dictionary.
    """
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Resolve environment variable placeholders
    def resolve_env(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, f"Missing env var: {env_var}")
        return value

    def resolve_recursive(obj):
        if isinstance(obj, dict):
            return {k: resolve_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve_recursive(v) for v in obj]
        else:
            return resolve_env(obj)

    return resolve_recursive(config)


def start_adapters(config, broker):
    """
    Initializes and starts all adapters based on the configuration.
    :param config: The loaded configuration dictionary.
    :param broker: Instance of the message broker.
    """
    # Start input adapters
    for input_adapter in config["inputs"]:
        if input_adapter["type"] == "smtp":
            smtp_adapter = SMTPAdapter(config=input_adapter, broker=broker)
            smtp_adapter.start()

    # Start output adapters
    for output_adapter in config["outputs"]:
        if output_adapter["type"] == "webhook":
            webhook_adapter = WebhookAdapter(config=output_adapter, broker=broker)
            asyncio.create_task(webhook_adapter.start())


if __name__ == "__main__":
    # Load environment variables and configuration
    load_dotenv()
    config = load_config()

    # RabbitMQ message broker configuration
    broker_config = config["broker"]

    # Initialize the message broker
    broker = MessageBroker(
        host=broker_config["host"],
        port=int(broker_config["port"]),
        username=broker_config["username"],
        password=broker_config["password"]
    )

    try:
        # Start adapters
        start_adapters(config, broker)
        print("NotifyStack is running. Press Ctrl+C to stop.")
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\nShutting down NotifyStack...")