import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope, AuthResult, LoginPassword
from core.message_broker import MessageBroker
from core.message_schema import Message
from logger import Logger


class SMTPHandler:
    """
    Custom handler for aiosmtpd to process incoming emails with optional authentication.
    """

    def __init__(self, broker: MessageBroker, valid_credentials: dict):
        self.logger = Logger.get_logger()
        self.broker = broker
        self.valid_credentials = valid_credentials
        self.authenticated_sessions = set()  # Track authenticated sessions
        self.logger.debug("SMTPHandler initialized with optional authentication.")

    async def handle_CONNECT(self, server, session, envelope):
        self.logger.debug(f"Client connected: {session.peer}")
        return '220 localhost SMTP ready'

    async def handle_AUTH(self, server, session, envelope, mechanism, auth_data):
        """
        Handles SMTP AUTH command to authenticate users.
        """
        self.logger.debug(f"Authentication requested with mechanism: {mechanism}")

        if mechanism != "LOGIN":
            self.logger.warning("Unsupported authentication mechanism.")
            return AuthResult(success=False, handled=False)

        if isinstance(auth_data, LoginPassword):
            username, password = auth_data.login.decode(), auth_data.password.decode()

            # Validate credentials
            if username in self.valid_credentials and self.valid_credentials[username] == password:
                self.authenticated_sessions.add(session)
                self.logger.info(f"User '{username}' authenticated successfully.")
                return AuthResult(success=True)
            else:
                self.logger.warning(f"Authentication failed for user '{username}'.")
                return AuthResult(success=False)

        self.logger.error("Invalid authentication data format.")
        return AuthResult(success=False)

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        """
        Handles RCPT command, validating recipients.
        """
        if not address.endswith('@example.com'):
            self.logger.info(f"Rejected email to {address}: not relaying to that domain")
            return '550 not relaying to that domain'

        envelope.rcpt_tos.append(address)

        if session in self.authenticated_sessions:
            self.logger.info(f"Accepted email to {address} from authenticated session.")
        else:
            self.logger.warning(f"Accepted email to {address} from unauthenticated session.")

        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        """
        Handles the DATA command and logs the email content.
        """
        self.logger.info(f"Message from: {envelope.mail_from}")
        self.logger.info(f"Message to: {envelope.rcpt_tos}")
        self.logger.info(f"Message content:\n{envelope.content.decode('utf-8')}")

        # Publish the message to the broker
        email_data = {
            "from": envelope.mail_from,
            "to": envelope.rcpt_tos,
            "content": envelope.content.decode("utf-8"),
        }
        
        message = Message(source="smtp", type="email", payload=email_data)
        self.broker.publish(queue="notifications", message=message.dict())

        if session in self.authenticated_sessions:
            self.logger.info(f"Email published to broker from authenticated session: {message.dict()}")
        else:
            self.logger.warning(f"Email published to broker from unauthenticated session: {message.dict()}")

        return '250 Message accepted for delivery'


class SMTPAdapter:
    """
    SMTP Adapter that listens on a specified port and processes emails using aiosmtpd.
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
        valid_credentials = self.config.get("credentials", {})
        smtp_handler = SMTPHandler(broker=self.broker, valid_credentials=valid_credentials)

        port = self.config.get("port", 587)
        try:
            self.controller = Controller(smtp_handler, hostname="0.0.0.0", port=port)
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