from aiosmtpd.controller import Controller
from core.message_broker import MessageBroker
from logger import Logger
from smtp_handler import SMTPHandler

class SMTPAdapter:
    """
    NotifyStack adapter for receiving emails via SMTP.

    :param config: The configuration dictionary for the SMTP adapter.
    :param broker: Instance of the message broker.

    The configuration dictionary should contain the following keys:
    - host: The hostname or IP address to bind to (default: localhost).
    - port: The port to listen on (default: 587).
    - useCredentials: A boolean indicating whether to require authentication (default: true).
    - (optional if ) credentials: A dictionary of valid username/password pairs for authentication.
    """

    def __init__(self, config, broker: MessageBroker):
        self.logger = Logger().get_logger()
        self.logger.debug("Initializing SMTP Adapter...")
        self.config = config
        self.broker = broker
        self.controller = None

    def start(self):
        """
        Starts the SMTP server on the specified port (default: 587).
        """
        
        # Validate SMTP configuration
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 587)

        # Initialize the SMTP handler
        self.logger.debug(f"Starting SMTP server on {host}:{port}...")
        smtp_handler = SMTPHandler(self.broker, self.config)
        
        try:
            self.controller = Controller(smtp_handler, hostname=host, port=port)
            self.controller.start()
            self.logger.info(f"SMTP server started on port {port}.")
        except Exception as e:
            self.logger.error(f"Failed to start SMTP server: {e}")
            raise

    def stop(self):
        """
        Stops the SMTP server gracefully.
        """
        if self.controller:
            self.controller.stop()
            self.logger.info("SMTP server stopped.")