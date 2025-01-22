from aiosmtpd.smtp import AuthResult, LoginPassword
from core.message_broker import MessageBroker
from classes.input.smtp_input_message import SMTPInputMessage
from classes.queue_types import QueueType
from classes.message_types import MessageType, MessageReceiver
from logger import Logger


class SMTPHandler:
    """
    Custom handler for aiosmtpd to process incoming emails with optional authentication.
    """

    def __init__(self, broker: MessageBroker, config: dict):
        """
        Initializes the SMTPHandler with the given settings.
        :param broker: MessageBroker instance for publishing messages.
        :param config: Dictionary containing SMTP configuration settings.
        """
        self.logger = Logger.get_logger()
        self.broker = broker
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 25)
        self.use_credentials = config.get("authentication", False)
        self.auth_type = config.get("auth_type", "plain")
        self.valid_credentials = {
            cred["email"]: cred["password"]
            for cred in config.get("credentials", [])
        }
        self.use_tls = config.get("tls", True)
        self.allow_relay = config.get("allow_relay", False)
        self.authenticated_sessions = set()

        self.logger.debug(
            f"SMTPHandler initialized with host={self.host}, port={self.port}, "
            f"use_credentials={self.use_credentials}, use_tls={self.use_tls}, "
            f"allow_relay={self.allow_relay}"
        )

    async def handle_CONNECT(self, server, session, envelope):
        """
        Handles the initial connection.
        """
        self.logger.debug(f"Client connected: {session.peer}")
        return f'220 {self.host} SMTP ready'

    async def handle_AUTH(self, server, session, envelope, mechanism, auth_data):
        """
        Handles SMTP AUTH command to authenticate users.
        """
        self.logger.debug(f"Authentication requested with mechanism: {mechanism}")

        if not self.use_credentials:
            self.logger.info("Authentication is disabled.")
            return AuthResult(success=True)

        if mechanism != "LOGIN":
            self.logger.warning("Unsupported authentication mechanism.")
            return AuthResult(success=False, handled=False)

        if isinstance(auth_data, LoginPassword):
            username, password = auth_data.login.decode(), auth_data.password.decode()
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
        if not self.allow_relay and not address.endswith('@example.com'):
            self.logger.info(f"Rejected email to {address}: not relaying to that domain.")
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
        self.logger.debug(f"Received email from {envelope.mail_from} to {envelope.rcpt_tos}")

        # Create an SMTPInputMessage object
        email_data = SMTPInputMessage(
            messageType=MessageType.INPUT,
            messageReceiver=MessageReceiver.PROCESSOR,
            sender=envelope.mail_from,
            recipient=envelope.rcpt_tos,
            subject=envelope.content.get('subject', 'No Subject'),
            body=envelope.content.get('body', ''),
        )

        # Publish the email data to the processing queue
        self.logger.debug(f"Publishing email data to the processing queue: {email_data.dict()}")
        self.logger.info(f"Email received from {envelope.mail_from} to {envelope.rcpt_tos}, publishing to processing queue.")
        self.broker.publish(queue=QueueType.PROCESSING, message=email_data)
        return '250 Message accepted for delivery'