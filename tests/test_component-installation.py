import unittest
import asyncio
import k8s as k8s
import path_searcher as path_builder
import provider as provider
from helm import CrossplaneHelmManager

loop = asyncio.get_event_loop()
manifests_path = path_builder.get_manifest_path()


class TestComponentInstallation(unittest.TestCase):

    # Test Case 1: Crossplane Installation Test
    # Objective:
    # Verify that Crossplane can be successfully installed on a clean cluster and operates without issues.
    # Preconditions:
    # Clean NMCCP cluster without any components installed.
    # Procedure:
    # Install Crossplane.
    # Postcondition:
    # Crossplane should be healthy and properly installed on the cluster.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    # ==================================================================================
    def test_crossplane_installation(self):
        # given
        loop.run_until_complete(CrossplaneHelmManager.install_crossplane_helm_chart())

        # when
        response_json = k8s.send_request(
            http_method="GET",
            api_path="api/v1/namespaces/crossplane-system/pods")

        # Assertions
        self.assertEqual(response_json['items'][0]['metadata']['namespace'], "crossplane-system")
        self.assertIn("crossplane", response_json['items'][0]['metadata']['name'])
        self.assertEqual(response_json['items'][0]['status']['phase'], "Running")

        self.assertEqual(response_json['items'][1]['metadata']['namespace'], "crossplane-system")
        self.assertIn("crossplane-rbac-manager", response_json['items'][1]['metadata']['name'])
        self.assertEqual(response_json['items'][1]['status']['phase'], "Running")

        loop.run_until_complete(CrossplaneHelmManager.uninstall_crossplane_helm_chart())

    # Test Case 2: Crossplane Provider Installation Test
    # Objective:
    # Verify the successful installation and operational health of the Kubernetes provider for Crossplane.
    # Preconditions:
    # Crossplane is installed and working correctly.
    # Procedure:
    # Install the Kubernetes provider for Crossplane.
    # Postcondition:
    # Kubernetes provider should be healthy and active.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    # ==================================================================================
    def test_provider_installation(self):
        # given
        provider.install_digital_ocean_provider()

        # when
        k8s.create_resource_from_yaml(
            f"{path_builder.get_manifest_path()}/digital_ocean/digital_ocean_provider.yaml")

        response_json = k8s.send_request("GET", "apis/pkg.crossplane.io/v1/providers/provider-digitalocean")

        # then
        self.assertEqual(response_json['metadata']['name'], "provider-digitalocean")

        conditions = {condition['type']: condition for condition in response_json['status']['conditions']}

        self.assertEqual(conditions.get("Installed", {}).get("status"), "True", "'Installed' condition is not True")
        self.assertEqual(conditions.get("Healthy", {}).get("status"), "True", "'Healthy' condition is not True")

        provider.uninstall_digital_ocean_provider()
