from __future__ import print_function

import requests
import yaml
import json
from kubernetes import client, config
from kubernetes.dynamic import DynamicClient
from logger import load_config, setup_logger
from path_searcher import get_config_path

config_file = get_config_path()
logger = setup_logger()


def load_config():
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def get_dynamic_kubernetes_client():
    kubeconfig = load_config().get('k8s', {}).get('kubeconfig_path', '')
    config.load_kube_config(config_file=kubeconfig)
    return DynamicClient(client.ApiClient())


def get_default_kubernetes_client():
    kubeconfig = load_config().get('k8s', {}).get('kubeconfig_path', '')
    config.load_kube_config(config_file=kubeconfig)
    return client.CoreV1Api()


def get_admin_token():
    config_data = load_config()
    return config_data.get('k8s', {}).get('admin-token', '')


def get_cluster_uri():
    config_data = load_config()
    return config_data.get('k8s', {}).get('cluster-uri', '')


def send_request_and_get_response(http_method, api_path):
    url = f"{get_cluster_uri()}/{api_path}"
    headers = {
        'Authorization': f"Bearer {get_admin_token()}"
    }
    response = requests.request(http_method, url, headers=headers, verify=False)
    return response


def send_request_and_get_json_response(http_method, api_path):
    url = f"{get_cluster_uri()}/{api_path}"
    headers = {
        'Authorization': f"Bearer {get_admin_token()}"
    }
    response = requests.request(http_method, url, headers=headers, verify=False)
    return response.json()


def create_resource_from_yaml(yaml_file_path):
    dynamic_client = get_dynamic_kubernetes_client()

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


def delete_resource_by(resource_type, resource_name, namespace="default"):
    dynamic_client = get_dynamic_kubernetes_client()

    try:
        resource_api = dynamic_client.resources.get(api_version='v1', kind=resource_type)

        resource_api.delete(name=resource_name, namespace=namespace)
        logger.info(f"Resource '{resource_type}' named '{resource_name}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete resource '{resource_type}' named '{resource_name}': {e}")


def delete_resource_by_file(yaml_file):
    dynamic_client = get_dynamic_kubernetes_client()

    try:
        # Load the YAML content
        with open(yaml_file, 'r') as f:
            resource_data = yaml.safe_load(f)

        # Extract resource type (kind), name, and namespace
        resource_type = resource_data.get("kind")
        resource_name = resource_data.get("metadata", {}).get("name")
        resource_namespace = resource_data.get("metadata", {}).get("namespace", "default")
        api_version = resource_data.get("api_version")

        if not resource_type or not resource_name:
            raise ValueError(f"Missing 'kind' or 'metadata.name' in the YAML file: {yaml_file}")

        # Get the appropriate resource API based on the resource type
        resource_api = dynamic_client.resources.get(api_version=api_version, kind=resource_type)

        # Delete the resource
        resource_api.delete(name=resource_name, namespace=resource_namespace)
        logger.info(
            f"Resource '{resource_type}' named '{resource_name}' deleted successfully from namespace '{resource_namespace}'.")

    except Exception as e:
        logger.error(f"Failed to delete resource from file '{yaml_file}': {e}")


def update_resource_parameters_with_namespace_from_yaml(yaml_file_path, updates):
    # Load the config file
    config = load_config()

    # Get Kubernetes configuration and API details from the config
    k8s_config = config.get('k8s', {})
    api_url = k8s_config.get('cluster-uri', '')
    admin_token = k8s_config.get('admin-token', '')

    try:
        # Read the YAML file and extract resource kind, name, and namespace
        with open(yaml_file_path, 'r') as f:
            resource_data = yaml.safe_load(f)

        resource_type = resource_data.get("kind")
        resource_name = resource_data.get("metadata", {}).get("name")
        resource_namespace = resource_data.get("metadata", {}).get("namespace", "default")
        api_version = resource_data.get("apiVersion")  # api_version key should be 'apiVersion'

        if not resource_type or not resource_name:
            raise ValueError(f"Missing 'kind' or 'metadata.name' in the YAML file: {yaml_file_path}")

        # Build the URL for the resource
        url = f"{api_url}/apis/{api_version}/namespaces/{resource_namespace}/{resource_type.lower()}s/{resource_name}"

        # Prepare the patch payload from the updates argument
        patch_operations = []
        for path, value in updates.items():
            patch_operations.append({
                "op": "replace",
                "path": path,
                "value": value
            })

        # Prepare headers for the request
        headers = {
            'Content-Type': 'application/json-patch+json',
            'Authorization': f'Bearer {admin_token}'
        }

        # Send PATCH request to update the resource
        response = requests.patch(url, headers=headers, data=json.dumps(patch_operations), verify=False)

        if response.status_code == 200:
            logger.info(
                f"Successfully updated resource '{resource_type}' named '{resource_name}' in namespace '{resource_namespace}'.")
        else:
            logger.error(f"Failed to update resource. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")

    except Exception as e:
        logger.error(f"Failed to update resource from file '{yaml_file_path}': {e}")


def update_cluster_resource_parameters(yaml_file_path, updates):
    # Load the config file
    config = load_config()

    # Get Kubernetes configuration and API details from the config
    k8s_config = config.get('k8s', {})
    api_url = k8s_config.get('cluster-uri', '')
    admin_token = k8s_config.get('admin-token', '')

    try:
        # Read the YAML file and extract resource kind, name, and namespace
        with open(yaml_file_path, 'r') as f:
            resource_data = yaml.safe_load(f)

        resource_type = resource_data.get("kind")
        resource_name = resource_data.get("metadata", {}).get("name")
        api_version = resource_data.get("apiVersion")  # api_version key should be 'apiVersion'

        if not resource_type or not resource_name:
            raise ValueError(f"Missing 'kind' or 'metadata.name' in the YAML file: {yaml_file_path}")

        # Build the URL for the resource
        url = f"{api_url}/apis/{api_version}/{resource_type.lower()}s/{resource_name}"

        # Prepare the patch payload from the updates argument
        patch_operations = []
        for path, value in updates.items():
            patch_operations.append({
                "op": "replace",
                "path": path,
                "value": value
            })

        # Prepare headers for the request
        headers = {
            'Content-Type': 'application/json-patch+json',
            'Authorization': f'Bearer {admin_token}'
        }

        # Send PATCH request to update the resource
        response = requests.patch(url, headers=headers, data=json.dumps(patch_operations), verify=False)

        if response.status_code == 200:
            logger.info(f"Successfully updated resource '{resource_type}' named '{resource_name}'")
        else:
            logger.error(f"Failed to update resource. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")

    except Exception as e:
        logger.error(f"Failed to update resource from file '{yaml_file_path}': {e}")
