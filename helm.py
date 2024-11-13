import yaml
from pyhelm3 import Client
from logger import load_config, setup_logger
from path_searcher import get_config_path

config_file = get_config_path()
logger = setup_logger()


def load_config(config_file: str):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


async def install_crossplane_helm_chart():
    config = load_config(config_file)

    helm_config = config.get('helm', {})
    k8s_config = config.get('k8s', {})

    kubeconfig = k8s_config.get('kubeconfig', '')
    kubecontext = k8s_config.get('kubecontext', '')
    chart_name = helm_config.get('chart_name', 'crossplane')
    repo = helm_config.get('repo', 'https://charts.crossplane.io/stable')
    version = helm_config.get('version', '1.17.2')
    namespace = helm_config.get('namespace', 'crossplane-system')
    install_crds = helm_config.get('install_crds', True)

    helm_client = Client(kubeconfig=kubeconfig, kubecontext=kubecontext)

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


async def uninstall_crossplane_helm_chart():
    config = load_config(config_file)

    k8s_config = config.get('k8s', {})
    kubeconfig = k8s_config.get('kubeconfig', '')
    kubecontext = k8s_config.get('kubecontext', '')
    namespace = config.get('helm', {}).get('namespace', 'crossplane-system')

    helm_client = Client(kubeconfig=kubeconfig, kubecontext=kubecontext)

    try:
        logger.info(f"Uninstalling release from namespace {namespace}...")
        await helm_client.uninstall_release("crossplane", namespace=namespace)
        logger.info("Release uninstalled successfully.")

    except Exception as e:
        logger.error(f"Failed to uninstall Helm release: {e}")
