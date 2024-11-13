import requests
import yaml
import json
from kubernetes import client, config
from kubernetes.dynamic import DynamicClient
from logger import LoggerManager
from config_loader import ConfigLoader

config_data = ConfigLoader.load_config()

# Setup logger
logger = LoggerManager.get_logger(config_data)


class KubernetesResourceManager:
    """
    Class for managing Kubernetes resources and interacting with the Kubernetes API.
    """

    @staticmethod
    def get_dynamic_kubernetes_client():
        """Returns a Dynamic Kubernetes client."""
        kubeconfig = config_data.get('k8s', {}).get('kubeconfig_path', '')
        config.load_kube_config(config_file=kubeconfig)
        return DynamicClient(client.ApiClient())

    @staticmethod
    def get_default_kubernetes_client():
        """Returns the default Kubernetes client (CoreV1Api)."""
        kubeconfig = config_data.get('k8s', {}).get('kubeconfig_path', '')
        config.load_kube_config(config_file=kubeconfig)
        return client.CoreV1Api()

    @staticmethod
    def get_admin_token():
        """Fetches the admin token from the config file."""
        return config_data.get('k8s', {}).get('admin-token', '')

    @staticmethod
    def get_cluster_uri():
        """Fetches the cluster URI from the config file."""
        return config_data.get('k8s', {}).get('cluster-uri', '')

    @staticmethod
    def send_request_and_get_response(http_method, api_path):
        """Sends an HTTP request to the Kubernetes API and returns the response."""
        url = f"{KubernetesResourceManager.get_cluster_uri()}/{api_path}"
        headers = {
            'Authorization': f"Bearer {KubernetesResourceManager.get_admin_token()}"
        }
        response = requests.request(http_method, url, headers=headers, verify=False)
        return response

    @staticmethod
    def send_request_and_get_json_response(http_method, api_path):
        """Sends an HTTP request to the Kubernetes API and returns the response as JSON."""
        url = f"{KubernetesResourceManager.get_cluster_uri()}/{api_path}"
        headers = {
            'Authorization': f"Bearer {KubernetesResourceManager.get_admin_token()}"
        }
        response = requests.request(http_method, url, headers=headers, verify=False)
        return response.json()

    @staticmethod
    def create_resource_from_yaml(yaml_file_path):
        """Creates a resource in Kubernetes from a given YAML file."""
        dynamic_client = KubernetesResourceManager.get_dynamic_kubernetes_client()
        try:
            with open(yaml_file_path, 'r') as f:
                yaml_content = yaml.safe_load(f)

            api_version = yaml_content.get("apiVersion")
            kind = yaml_content.get("kind")

            resource_api = dynamic_client.resources.get(api_version=api_version, kind=kind)
            resource_api.create(body=yaml_content)
            logger.info(f"Resource '{kind}' created successfully from {yaml_file_path}.")
        except Exception as e:
            logger.error(f"Failed to create resource from {yaml_file_path}: {e}")

    @staticmethod
    def delete_resource_by(resource_type, resource_name, namespace="default"):
        """Deletes a Kubernetes resource by its type, name, and optional namespace."""
        dynamic_client = KubernetesResourceManager.get_dynamic_kubernetes_client()
        try:
            resource_api = dynamic_client.resources.get(api_version='v1', kind=resource_type)
            resource_api.delete(name=resource_name, namespace=namespace)
            logger.info(f"Resource '{resource_type}' named '{resource_name}' deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete resource '{resource_type}' named '{resource_name}': {e}")

    @staticmethod
    def delete_resource_by_file(yaml_file):
        """Deletes a Kubernetes resource using a YAML file."""
        dynamic_client = KubernetesResourceManager.get_dynamic_kubernetes_client()
        try:
            with open(yaml_file, 'r') as f:
                resource_data = yaml.safe_load(f)

            resource_type = resource_data.get("kind")
            resource_name = resource_data.get("metadata", {}).get("name")
            resource_namespace = resource_data.get("metadata", {}).get("namespace", "default")
            api_version = resource_data.get("api_version")

            if not resource_type or not resource_name:
                raise ValueError(f"Missing 'kind' or 'metadata.name' in the YAML file: {yaml_file}")

            resource_api = dynamic_client.resources.get(api_version=api_version, kind=resource_type)
            resource_api.delete(name=resource_name, namespace=resource_namespace)
            logger.info(
                f"Resource '{resource_type}' named '{resource_name}' deleted successfully from namespace '{resource_namespace}'.")
        except Exception as e:
            logger.error(f"Failed to delete resource from file '{yaml_file}': {e}")

    @staticmethod
    def delete_cluster_resource_by_file(yaml_file):
        """Deletes a Kubernetes resource using a YAML file."""
        try:
            # Load resource data from the YAML file
            with open(yaml_file, 'r') as f:
                resource_data = yaml.safe_load(f)

            # Get basic resource information
            resource_type = resource_data.get("kind")
            resource_name = resource_data.get("metadata", {}).get("name")
            api_version = resource_data.get("apiVersion")
            admin_token = config_data.get('k8s', {}).get('admin-token', '')
            api_url = config_data.get('k8s', {}).get('cluster-uri', '')

            if not resource_type or not resource_name:
                raise ValueError(f"Missing 'kind' or 'metadata.name' in the YAML file: {yaml_file}")

            headers = {
                'Authorization': f'Bearer {admin_token}',
                "Content-Type": "application/json"
            }

            url = f"{api_url}/apis/{api_version}/{resource_type.lower()}s/{resource_name}"

            # Send the DELETE request
            response = requests.delete(url, headers=headers, verify=False)

            # Check the response status
            if response.status_code == 200 or response.status_code == 202:
                logger.info(
                    f"Resource '{resource_type}' named '{resource_name}' deleted successfully")
            else:
                logger.error(f"Failed to delete resource '{resource_name}': {response.text}")

        except Exception as e:
            logger.error(f"Failed to delete resource from file '{yaml_file}': {e}")

    @staticmethod
    def update_resource_parameters_with_namespace_from_yaml(yaml_file_path, updates):
        """Updates a Kubernetes resource from a YAML file using PATCH request."""
        api_url = config_data.get('k8s', {}).get('cluster-uri', '')
        admin_token = config_data.get('k8s', {}).get('admin-token', '')

        try:
            with open(yaml_file_path, 'r') as f:
                resource_data = yaml.safe_load(f)

            resource_type = resource_data.get("kind")
            resource_name = resource_data.get("metadata", {}).get("name")
            resource_namespace = resource_data.get("metadata", {}).get("namespace", "default")
            api_version = resource_data.get("apiVersion")

            if not resource_type or not resource_name:
                raise ValueError(f"Missing 'kind' or 'metadata.name' in the YAML file: {yaml_file_path}")

            url = f"{api_url}/apis/{api_version}/namespaces/{resource_namespace}/{resource_type.lower()}s/{resource_name}"
            patch_operations = [{"op": "replace", "path": path, "value": value} for path, value in updates.items()]

            headers = {
                'Content-Type': 'application/json-patch+json',
                'Authorization': f'Bearer {admin_token}'
            }

            response = requests.patch(url, headers=headers, data=json.dumps(patch_operations), verify=False)

            if response.status_code == 200:
                logger.info(
                    f"Successfully updated resource '{resource_type}' named '{resource_name}' in namespace '{resource_namespace}'.")
            else:
                logger.error(f"Failed to update resource. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
        except Exception as e:
            logger.error(f"Failed to update resource from file '{yaml_file_path}': {e}")

    @staticmethod
    def update_cluster_resource_parameters(yaml_file_path, updates):
        """Updates a Kubernetes cluster resource from a YAML file using PATCH request."""
        api_url = config_data.get('k8s', {}).get('cluster-uri', '')
        admin_token = config_data.get('k8s', {}).get('admin-token', '')

        try:
            with open(yaml_file_path, 'r') as f:
                resource_data = yaml.safe_load(f)

            resource_type = resource_data.get("kind")
            resource_name = resource_data.get("metadata", {}).get("name")
            api_version = resource_data.get("apiVersion")

            if not resource_type or not resource_name:
                raise ValueError(f"Missing 'kind' or 'metadata.name' in the YAML file: {yaml_file_path}")

            url = f"{api_url}/apis/{api_version}/{resource_type.lower()}s/{resource_name}"
            patch_operations = [{"op": "replace", "path": path, "value": value} for path, value in updates.items()]

            headers = {
                'Content-Type': 'application/json-patch+json',
                'Authorization': f'Bearer {admin_token}'
            }

            response = requests.patch(url, headers=headers, data=json.dumps(patch_operations), verify=False)

            if response.status_code == 200:
                logger.info(f"Successfully updated resource '{resource_type}' named '{resource_name}'")
            else:
                logger.error(f"Failed to update resource. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
        except Exception as e:
            logger.error(f"Failed to update resource from file '{yaml_file_path}': {e}")
