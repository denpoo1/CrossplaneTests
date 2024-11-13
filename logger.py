import logging
import yaml

config_file = "/resourses/config.yaml"

def load_config(config_file: str):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def setup_logger():
    config = load_config(config_file)
    logging_enabled = config.get('k8s', {}).get('logging', True) or config.get('helm', {}).get('logging', True) or config.get('provider', {}).get('logging', True)

    if logging_enabled:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.disable(logging.CRITICAL)

    return logging.getLogger(__name__)
