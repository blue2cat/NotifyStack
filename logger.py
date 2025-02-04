import logging
import os

class Logger:
    """
    Global static logger class used to log messages across the application
    """
    _logger = None

    @staticmethod
    def get_logger():
        """
        Return a logger instance
        """
        if Logger._logger is None:
            Logger._logger = logging.getLogger("NotifyStack")
            Logger._logger.setLevel(logging.DEBUG)

            # Avoid duplicate handlers
            if not Logger._logger.hasHandlers():
                # Console Handler
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] [%(processName)s] %(message)s"
                )
                console_handler.setFormatter(console_formatter)
                Logger._logger.addHandler(console_handler)

                # File Handler
                log_file = os.getenv("LOG_FILE", "notifystack.log")
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.INFO)
                file_formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] [%(processName)s] %(message)s"
                )
                file_handler.setFormatter(file_formatter)
                Logger._logger.addHandler(file_handler)
        return Logger._logger
    