import yaml
from k8s import get_dynamic_kubernetes_client
from logger import load_config, setup_logger
from path_searcher import get_config_path

config_file = get_config_path()
logger = setup_logger()

def load_config():
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def install_digital_ocean_provider():
    config_data = load_config()

    provider_config = config_data.get('provider', {})

    provider_yaml_file = provider_config.get('provider_config', '')
    provider_name = provider_config.get('name', 'digital_ocean')

    dynamic_client = get_dynamic_kubernetes_client()

    try:
        with open(provider_yaml_file, 'r') as f:
            yaml_content = yaml.safe_load(f)

        provider_api = dynamic_client.resources.get(api_version='pkg.crossplane.io/v1', kind='Provider')

        provider_api.create(body=yaml_content, namespace="crossplane-system")
        logger.info(f"Digital Ocean Provider '{provider_name}' applied successfully.")
    except Exception as e:
        logger.error(f"Failed to apply Digital Ocean Provider: {e}")


def uninstall_digital_ocean_provider():
    config_data = load_config()

    provider_config = config_data.get('provider', {})

    provider_name = provider_config.get('name', 'digital_ocean')

    dynamic_client = get_dynamic_kubernetes_client()

    try:
        provider_api = dynamic_client.resources.get(api_version='pkg.crossplane.io/v1', kind='Provider')

        provider_api.delete(name=provider_name, namespace="crossplane-system")
        logger.info(f"Digital Ocean Provider '{provider_name}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete Digital Ocean Provider '{provider_name}': {e}")
