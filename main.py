import os
import asyncio
import signal
from dotenv import load_dotenv
import yaml
from core.message_broker import MessageBroker
from core.processor import Processor
from adapters.input.smtp.smtp_adapter import SMTPAdapter

def load_config():
    """
    Loads the YAML configuration and resolves placeholders using environment variables.
    """
    try:
        with open("config.yaml", "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print("Config file not found. Please ensure a 'config.yaml' file exists in the root directory.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing the config file: {e}")
        exit(1)

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

def start_adapters(adapter_config, message_broker):
    """
    Initializes and starts all adapters based on the configuration.
    :param config: The loaded configuration dictionary.
    :param broker: Instance of the message broker.
    :param processor: Instance of the Processor.
    """
    input_tasks = []

    for input_adapter in adapter_config["inputs"]:
        if input_adapter["type"].match("smtp*"):
            smtp_adapter = SMTPAdapter(config=input_adapter, broker=message_broker,)
            input_tasks.append(asyncio.create_task(smtp_adapter.start()))

    return input_tasks


async def shutdown(sig, loop, tasks):
    """
    Gracefully shutdown all adapters and the event loop.
    :param signal: The signal received (e.g., SIGINT).
    :param loop: The asyncio event loop.
    :param tasks: The list of tasks to cancel.
    """
    print(f"Received exit signal {sig.name}... Shutting down.")
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


if __name__ == "__main__":
    load_dotenv()
    config = load_config()

    broker_config = config["broker"]
    broker = MessageBroker(
        host=broker_config["host"],
        port=int(broker_config["port"]),
        username=broker_config["username"],
        password=broker_config["password"]
    )

    # Initialize Processor
    processor = Processor(config["outputs"], config["routes"], broker)

    # Start NotifyStack
    try:
        loop = asyncio.get_event_loop()

        # Start adapters
        adapter_tasks = start_adapters(config, broker)

        # Handle shutdown signals
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig:
                                     asyncio.create_task(shutdown(s, loop, adapter_tasks)))

        print("NotifyStack is running. Press Ctrl+C to stop.")
        loop.run_forever()
    except (OSError, asyncio.CancelledError, yaml.YAMLError) as e:
        print(f"Error: {e}")
    finally:
        print("\nShutting down NotifyStack...")
