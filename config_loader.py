import yaml
import path_searcher as path_builder
from logger import LoggerManager


class ConfigLoader:

    @staticmethod
    def load_config():

        config_file = path_builder.get_config_path()

        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)

            # Initialize logger with the config data
            logger = LoggerManager.get_logger(config_data)

            return config_data
        except Exception as e:
            if 'logger' in locals():
                logger.error(f"Failed to load config from {config_file}: {e}")
            else:
                print(f"Failed to load config from {config_file}: {e}")
            raise
