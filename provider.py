import yaml
import path_searcher as path_builder
from logger import LoggerManager
from path_searcher import get_config_path
from k8s import KubernetesResourceManager
from config_loader import ConfigLoader

config_data_file = get_config_path()
config_data = ConfigLoader.load_config()
manifests_path = path_builder.get_manifest_path()

# Setup logger
logger = LoggerManager.get_logger(config_data)


def install_digital_ocean_provider():
    provider_config = config_data.get('provider', {})

    provider_yaml_file = provider_config.get('provider_config', '')
    provider_name = provider_config.get('name', 'digital_ocean')

    dynamic_client = KubernetesResourceManager.get_dynamic_kubernetes_client()

    try:
        with open(provider_yaml_file, 'r') as f:
            yaml_content = yaml.safe_load(f)

        provider_api = dynamic_client.resources.get(api_version='pkg.crossplane.io/v1', kind='Provider')

        provider_api.create(body=yaml_content, namespace="crossplane-system")
        logger.info(f"Digital Ocean Provider '{provider_name}' applied successfully.")
    except Exception as e:
        logger.error(f"Failed to apply Digital Ocean Provider: {e}")


def uninstall_digital_ocean_provider():
    provider_config = config_data.get('provider', {})

    provider_name = provider_config.get('name', 'provider-digitalocean')

    try:

        KubernetesResourceManager.delete_cluster_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_provider.yaml"
        )

        logger.info(f"Digital Ocean Provider '{provider_name}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete Digital Ocean Provider '{provider_name}': {e}")


def setup_digital_ocean_provider():
    try:
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_provider_config.yaml")
    except Exception as e:
        logger.error(f"Failed to Set Up Digital Ocean Provider: {e}")
