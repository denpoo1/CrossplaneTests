import logging

class LoggerManager:
    """
    Class to manage logging configuration.
    """
    @staticmethod
    def get_logger(config_data):
        """
        Set up and return a logger based on the configuration.
        """
        # Check if logging is enabled
        logging_enabled = (
                config_data.get('k8s', {}).get('logging', True)
                or config_data.get('helm', {}).get('logging', True)
                or config_data.get('provider', {}).get('logging', True)
        )

        # Set logging level
        if logging_enabled:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.disable(logging.CRITICAL)

        return logging.getLogger(__name__)
