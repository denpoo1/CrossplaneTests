import path_searcher as path_builder

from pyhelm3 import Client
from path_searcher import get_config_path
from config_loader import ConfigLoader
from logger import LoggerManager

config_data_file = get_config_path()
config_data = ConfigLoader.load_config()
manifests_path = path_builder.get_manifest_path()

# Setup logger
logger = LoggerManager.get_logger(config_data)


class CrossplaneHelmManager:

    @staticmethod
    async def install_crossplane_helm_chart():
        """
        Installs or upgrades the Crossplane Helm chart.
        """
        helm_config_data = config_data.get('helm', {})

        kubeconfig_path = helm_config_data.get('kubeconfig_path')
        chart_name = helm_config_data.get('chart_name', 'crossplane')
        repo = helm_config_data.get('repo', 'https://charts.crossplane.io/stable')
        version = helm_config_data.get('version', '1.17.2')
        namespace = helm_config_data.get('namespace', 'crossplane-system')
        install_crds = helm_config_data.get('install_crds', True)

        helm_client = Client(kubeconfig=kubeconfig_path)

        try:
            chart = await helm_client.get_chart(chart_name, repo=repo, version=version)

            revision = await helm_client.install_or_upgrade_release(
                chart_name,
                chart,
                {"installCRDs": install_crds},
                atomic=True,
                wait=True,
                create_namespace=True,
                namespace=namespace
            )

            logger.info(f"Release {revision.release.name} in namespace {revision.release.namespace} "
                        f"with revision {revision.revision} is {revision.status}")
        except Exception as e:
            logger.error(f"Failed to install or upgrade Helm release: {e}")
            raise

    @staticmethod
    async def uninstall_crossplane_helm_chart():
        """
        Uninstalls the Crossplane Helm chart from the Kubernetes cluster.
        """
        k8s_config_data = config_data.get('k8s', {})
        kubeconfig_path = k8s_config_data.get('kubeconfig_path')
        namespace = config_data.get('helm', {}).get('namespace', 'crossplane-system')

        helm_client = Client(kubeconfig=kubeconfig_path)

        try:
            logger.info(f"Uninstalling release from namespace {namespace}...")
            await helm_client.uninstall_release("crossplane", namespace=namespace)
            logger.info("Release uninstalled successfully.")
        except Exception as e:
            logger.error(f"Failed to uninstall Helm release: {e}")
            raise
