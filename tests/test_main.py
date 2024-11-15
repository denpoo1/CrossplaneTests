import time
import unittest
import path_searcher as path_builder

from k8s import KubernetesResourceManager

manifests_path = path_builder.get_manifest_path()


class TestMain(unittest.TestCase):

    # Test Case 16: Composite Resource Claim Creation Test
    # Preconditions:
    # Valid XRC YAML file is available.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Apply the XRC YAML file.
    # Confirm creation of the following:
    # Composite Resource Claim (XRC).
    # Composite Resource (XR).
    # Managed Resource(s) linked to the XRC.
    # Verify that the resources are created successfully on the target cluster.
    # Postcondition:
    # Check that XRC, XR, and Managed Resource(s) are present and functioning on the target cluster.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_claim_creation(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")

        # when
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")
        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                     "apis/compute.crossplane.io/v1alpha1/namespaces/default/dropletclaims/test-droplet-claim-1")

        # then
        self.assertEqual(response_json['metadata']['name'], "test-droplet-claim-1")

        conditions = {condition['type']: condition for condition in response_json['status']['conditions']}
        self.assertEqual(conditions.get("Synced", {}).get("status"), "True", "'Synced' condition is not True")
        self.assertEqual(conditions.get("Ready", {}).get("status"), "True", "'Ready' condition is not True")

        # post condition
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")

    # Test Case 17: Composite Resource Claim Update Test
    # Preconditions:
    # Valid XRC YAML file is available.
    # Modified version of the XRC YAML file with changes is available.
    #     Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Apply the original XRC YAML file.
    # Apply the modified XRC YAML file.
    # Confirm updates to:
    # Composite Resource Claim (XRC).
    # Composite Resource (XR).
    # Managed Resource(s) linked to the XRC.
    # Check the updated resources' status on the target cluster.
    # Postconditions:
    # Verify that the updated XRC, XR, and Managed Resource(s) reflect the changes and are correctly updated on the target cluster.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_claim_updating(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")

        # when
        updates = {
            "/spec/parameters/size": "s-2vcpu-2gb",
            "/spec/parameters/image": "ubuntu-20-04-x64"
        }
        KubernetesResourceManager.update_resource_parameters_with_namespace_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_claim_update.yaml",
            updates)

        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                     "apis/compute.crossplane.io/v1alpha1/namespaces/default/dropletclaims/test-droplet-claim-1")

        # then
        self.assertEqual(response_json['metadata']['name'], "test-droplet-claim-1")
        self.assertEqual(response_json['spec']['parameters']['size'], "s-2vcpu-2gb")

        conditions = {condition['type']: condition for condition in response_json['status']['conditions']}
        self.assertEqual(conditions.get("Synced", {}).get("status"), "True", "'Synced' condition is not True")
        self.assertEqual(conditions.get("Ready", {}).get("status"), "True", "'Ready' condition is not True")

        # post condition
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")

    # Test Case 18: Composite Resource Claim Deletion Test
    # Preconditions:
    # Valid XRC YAML file is available.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Apply the XRC YAML file.
    # Delete the XRC.
    # Confirm deletion of:
    # Composite Resource Claim (XRC).
    # Composite Resource (XR).
    # Managed Resource(s) linked to the XRC.
    # Verify the state on the target cluster to ensure all related resources are removed.
    # Postcondition:
    # Confirm that the XRC, XR, and Managed Resource(s) have been successfully deleted from the target cluster.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_claim_deleting(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")

        # when
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")

        response = KubernetesResourceManager.send_request_and_get_response("GET",
                                                                           "apis/compute.crossplane.io/v1alpha1/namespaces/default/dropletclaims/test-droplet-claim-1")

        # then
        self.assertEqual(response.status_code, 404)

        # post condition
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")

    # Test Case 6: Provider Permission Limitation Test
    # Objective:
    # Verify that the Provider has access only to required resources and cannot access unauthorized resources.
    def test_provider_permission_limitation(self):
        # when
        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                     "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean")
        full_provider_name = response_json["status"]["currentRevision"]
        provider_cluster_role_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", f"/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:system")

        # then
        for rule in provider_cluster_role_json['rules']:
            api_groups = rule.get('api_groups', [])
            self.assertNotIn('apps', api_groups, "'apps' should not be in api_groups")

    # Test Case 7: Role Aggregation Functionality Test
    # and
    # Test Case 26: Role Aggregation Functionality Test
    # Objective:
    # Verify Crossplane’s correct use of aggregated roles for accessing provider resources.
    def test_role_aggregation_functionality(self):
        # when
        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                     "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean")
        full_provider_name = response_json["status"]["currentRevision"]
        provider_cluster_role_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                                  "/apis/rbac.authorization.k8s.io/v1/clusterroles")

        # Filter roles by provider prefix
        provider_prefix = f"crossplane:provider:{full_provider_name}"
        role_names = {item["metadata"]["name"] for item in provider_cluster_role_json["items"]
                      if item["metadata"]["name"].startswith(provider_prefix)}

        # then
        self.assertEqual(len(role_names), 3)

    # Test Case 8: Restricted Secret Access Test
    # and
    # Test Case 20: Access to Secrets Test
    # and
    # Test Case 25: Provider Permission Limitation Test
    # and
    # Test Case 27: Restricted Secret Access Test
    # Objective:
    # Ensure that Crossplane, RBAC Manager, and Provider cannot access secrets outside their own namespace or label scope.
    # Preconditions:
    # Secrets with specific namespaces or labels are created exclusively for Crossplane, RBAC Manager, and Provider.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Attempt to access secrets outside the designated namespaces or labels using Crossplane, RBAC Manager, and Provider service accounts.
    # Postcondition:
    # Each service account should only access secrets within its authorized namespace or with the appropriate labels, maintaining isolation and security.
    # Cleanup:
    # Delete all Crossplane components created for this test, including all Crossplane components created by Crossplane itself.
    def test_restricted_secret_access(self):
        # when
        response_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean"
        )
        full_provider_name = response_json["status"]["currentRevision"]

        # Fetch the ClusterRoles for provider system, crossplane, and crossplane-rbac-manager
        provider_role = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", f"/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:system"
        )
        crossplane_role = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", "/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane"
        )
        rbac_manager_role = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", "/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane-rbac-manager"
        )

        # then
        # Define helper to filter 'secrets' access rules
        def extract_secret_rules(role_json):
            return [
                {
                    "verbs": rule.get("verbs", []),
                    "api_groups": rule.get("apiGroups", []),
                    "resources": rule.get("resources", []),
                }
                for rule in role_json.get("rules", [])
                if "secrets" in rule.get("resources", [])
            ]

        # Extract secret access rules for each role
        secret_access_roles = {
            "provider": extract_secret_rules(provider_role),
            "crossplane": extract_secret_rules(crossplane_role),
            "rbac_manager": extract_secret_rules(rbac_manager_role),
        }

        # Assertions to verify restricted access rules
        # Check provider role
        self.assertEqual(
            len(secret_access_roles["provider"]), 1,
            "Expected one 'secrets' access rule in provider role."
        )
        self.assertEqual(
            secret_access_roles["provider"][0]["verbs"], ["*"],
            "Provider role should have all permissions (*) for secrets."
        )
        self.assertIn(
            "", secret_access_roles["provider"][0]["api_groups"],
            "Provider role should have access to the empty API group for secrets."
        )

        # Check crossplane role
        self.assertEqual(
            len(secret_access_roles["crossplane"]), 1,
            "Expected one 'secrets' access rule in crossplane role."
        )
        self.assertEqual(
            secret_access_roles["crossplane"][0]["verbs"],
            ["get", "list", "watch", "create", "update", "patch", "delete"],
            "Crossplane role should have limited permissions for secrets."
        )
        self.assertEqual(
            secret_access_roles["crossplane"][0]["api_groups"],
            [""],
            "Crossplane role should have access only to the empty API group for secrets."
        )

        # Check RBAC Manager role
        self.assertEqual(
            len(secret_access_roles["rbac_manager"]), 0,
            "RBAC Manager role should not have access to secrets."
        )

    # Test Case 9: XRD Creation Test
    # Objective: Verify that an XRD (Composite Resource Definition) is correctly created in the cluster.
    # Preconditions:
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # A valid XRD YAML file is available.
    def test_xrd_create(self):
        # given
        xrd_yaml_path = f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"

        # when
        KubernetesResourceManager.create_resource_from_yaml(xrd_yaml_path)

        response_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", "/apis/apiextensions.crossplane.io/v1/compositeresourcedefinitions/xdroplets.compute.crossplane.io"
        )

        # then
        self.assertEqual(response_json["metadata"]["name"], "xdroplets.compute.crossplane.io")
        conditions = {condition["type"]: condition for condition in response_json["status"]["conditions"]}
        self.assertIn(conditions.get("Established", {}).get("status"), [True, False],
                      "'Established' condition is not True or False")
        self.assertIn(conditions.get("Offered", {}).get("status"), [True, False],
                      "'Offered' condition is not True or False")

        # post condition
        KubernetesResourceManager.delete_resource_by_file(xrd_yaml_path)

    # Test Case 10: XRD Update Test
    # Objective: Ensure that an update to an existing XRD is applied correctly, reflecting the changes in the cluster.
    # Preconditions:
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # A valid XRD YAML file is available.
    def test_xrd_updating(self):
        # given
        xrd_yaml_path = f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        KubernetesResourceManager.create_resource_from_yaml(xrd_yaml_path)

        # when
        initial_response_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", "/apis/apiextensions.crossplane.io/v1/compositeresourcedefinitions/xdroplets.compute.crossplane.io"
        )

        initial_default_image = \
            initial_response_json["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"][
                "properties"][
                "parameters"]["properties"]["image"]["default"]
        self.assertEqual(initial_default_image, "ubuntu-20-04-x64",
                         "Initial default image should be 'ubuntu-20-04-x64'.")

        # Apply updates to change the default image
        updates = {
            "/spec/versions/0/schema/openAPIV3Schema/properties/spec/properties/parameters/properties/image/default": "fedora"
        }
        KubernetesResourceManager.update_cluster_resource_parameters(xrd_yaml_path, updates)

        # Retrieve updated XRD
        updated_response_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", "/apis/apiextensions.crossplane.io/v1/compositeresourcedefinitions/xdroplets.compute.crossplane.io"
        )

        # then
        updated_default_image = \
            updated_response_json["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"][
                "properties"][
                "parameters"]["properties"]["image"]["default"]
        self.assertEqual(updated_default_image, "fedora", "Expected updated default image to be 'fedora'.")

        # post condition
        KubernetesResourceManager.delete_resource_by_file(xrd_yaml_path)

    # ==================================================================================
    # Test Case 11: XRD Deletion Test
    # Objective: Confirm that deleting an XRD removes it from the cluster.
    # Preconditions:
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # A valid XRD YAML file is available.
    # Procedure:
    # Apply the XRD YAML file.
    # Delete the XRD.
    # Postcondition:
    # Verify that the XRD is deleted from the cluster to ensure it no longer exists.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    # ==================================================================================
    def test_xrd_deleting(self):
        # given
        xrd_yaml_path = f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        KubernetesResourceManager.create_resource_from_yaml(xrd_yaml_path)

        # when
        KubernetesResourceManager.delete_resource_by_file(xrd_yaml_path)
        remove_response_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                            "/apis/apiextensions.crossplane.io/v1/compositeresourcedefinitions/xdroplets.compute.crossplane.io")

        # then
        self.assertEqual(remove_response_json['metadata']['name'], "xdroplets.compute.crossplane.io")
        conditions = {condition['type']: condition for condition in remove_response_json['status']['conditions']}
        self.assertEqual(conditions.get("Established", {}).get("status"), "False",
                         "'Established' condition is not False")
        self.assertEqual(conditions.get("Offered", {}).get("status"), "False", "'Offered' condition is not False")

    # ==================================================================================
    # Test Case 12: XRD Cluster Role Aggregation Test
    # Objective: Validate that creating an XRD triggers the creation of related aggregated cluster roles in the cluster.
    # Preconditions:
    # A valid XRD YAML file is available.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Apply the XRD YAML file.
    # Postcondition:
    # Verify that cluster roles related to XRD aggregation are created.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    # ==================================================================================
    def test_xrd_cluster_role_aggregation(self):
        # given
        xrd_yaml_path = f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        KubernetesResourceManager.create_resource_from_yaml(xrd_yaml_path)

        # when
        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                     "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean")
        full_provider_name = response_json["status"]["currentRevision"]

        provider_aggregate_to_edit_role_json = KubernetesResourceManager.send_request_and_get_response("GET",
                                                                                                       f"apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:aggregate-to-edit")
        provider_aggregate_to_view_role_json = KubernetesResourceManager.send_request_and_get_response("GET",
                                                                                                       f"apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:aggregate-to-view")
        provider_aggregate_system_role_json = KubernetesResourceManager.send_request_and_get_response("GET",
                                                                                                      f"apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:system")

        # then
        self.assertEqual(provider_aggregate_to_edit_role_json.status_code, 200)
        self.assertEqual(provider_aggregate_to_view_role_json.status_code, 200)
        self.assertEqual(provider_aggregate_system_role_json.status_code, 200)

        # post condition
        KubernetesResourceManager.delete_resource_by_file(xrd_yaml_path)

    # ==================================================================================
    # Test Case 14: Composition Update Test
    # Objective: Verify that updating a Composition correctly reflects the changes and continues to work as expected.
    # Preconditions:
    # The XRD for the Composition exists.
    # The Composition has been previously created.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # A valid XRD YAML file is available.
    # Procedure:
    # Update the Composition by applying a modified Composition YAML file.
    # Postcondition:
    # Confirm that the Composition reflects the updates by checking its status and configuration.
    # Ensure the Composition functions as expected with the new changes.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    # ==================================================================================
    def test_xr_updating(self):
        # given
        xr_yaml_path = f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml"
        KubernetesResourceManager.create_resource_from_yaml(xr_yaml_path)

        # when
        response_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET",
            "/apis/apiextensions.crossplane.io/v1/compositions/xdroplet-composition"
        )
        initial_volume_size_default = response_json["spec"]["resources"][0]["base"]["spec"]["forProvider"]["size"]
        self.assertEqual(initial_volume_size_default, "s-1vcpu-1gb",
                         "Initial default volume size should be 's-1vcpu-1gb'.")

        updates = {
            "/spec/resources/0/base/spec/forProvider/size": "s-1vcpu-2gb"
        }
        KubernetesResourceManager.update_cluster_resource_parameters(xr_yaml_path, updates)

        # then
        response_updated_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET",
            "/apis/apiextensions.crossplane.io/v1/compositions/xdroplet-composition"
        )
        updated_volume_size = response_updated_json["spec"]["resources"][0]["base"]["spec"]["forProvider"]["size"]
        self.assertEqual(updated_volume_size, "s-1vcpu-2gb",
                         "Updated default volume size should be 's-1vcpu-2gb'.")

        # post condition
        KubernetesResourceManager.delete_resource_by_file(xr_yaml_path)

    # ==================================================================================
    # Test Case 19: CRUD Permission Test
    # Objective: Verify that only authorized users can perform CRUD operations on Crossplane resources.
    # Preconditions:
    # Valid ClusterRole and ClusterRoleBinding configurations for Crossplane are in place.
    # An authorized user is available for testing CRUD operations.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Attempt to perform Create, Read, Update, and Delete (CRUD) operations on Crossplane resources using the authorized user.
    # Verify that unauthorized users cannot perform CRUD operations.
    # Check that no ClusterRoles are erroneously bound to unauthorized users.
    # Postcondition:
    # Confirm that only authorized users have CRUD access to Crossplane resources.
    # Ensure ClusterRoles related to Crossplane are not bound to unauthorized users.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    # ==============================================================================
    def test_role_permissions_by_name(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/shared_resourses/role.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/shared_resourses/role_binding.yaml")

        # when
        role_name = "crossplane-edit"
        namespace = "example-namespace"
        role_api_path = f"/apis/rbac.authorization.k8s.io/v1/namespaces/{namespace}/roles/{role_name}"
        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET", role_api_path)

        # then
        self.assertEqual(response_json['metadata']['name'], role_name, f"Role {role_name} does not exist")
        role_rules = response_json.get('rules', [])
        expected_permissions = [
            {"resource": "events", "verbs": ["get", "list", "watch"], "api_group": ""},
            {"resource": "secrets", "verbs": ["*"], "api_group": ""},
            {"resource": "dropletclaims", "verbs": ["*"], "api_group": "compute.crossplane.io"}
        ]

        def has_all_permissions_for_resource(resource, expected_verbs, api_group):
            return any(
                api_group in rule.get("apiGroups", [])
                and resource in rule.get("resources", [])
                and all(verb in rule.get("verbs", []) for verb in expected_verbs)
                for rule in role_rules
            )

        for permission in expected_permissions:
            resource = permission["resource"]
            expected_verbs = permission["verbs"]
            api_group = permission["api_group"]
            has_permission = has_all_permissions_for_resource(resource, expected_verbs, api_group)
            self.assertTrue(has_permission,
                            f"Role {role_name} does not have the expected permissions for {resource} with verbs {expected_verbs}")

        # post condition
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/shared_resourses/role.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/shared_resourses/role_binding.yaml")

    # ==================================================================================
    # Test Case 21: Access to ConfigMaps Test
    # Objective: Ensure that Crossplane, the RBAC Manager, and the Provider do not have access to ConfigMaps outside their scope.
    # Preconditions:
    # Service accounts for Crossplane, RBAC Manager, and Provider are set up.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Attempt to access ConfigMaps not associated with Crossplane, RBAC Manager, or Provider using their respective service accounts.
    # Postcondition:
    # Confirm that Crossplane, RBAC Manager, and Provider service accounts cannot access ConfigMaps beyond their required scope.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    # ==================================================================================
    def test_restricted_configmap_access(self):
        # given
        provider_path = "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean"
        provider_role_path = "/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:system"
        crossplane_role_path = "/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane"
        rbac_manager_role_path = "/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane-rbac-manager"

        # when
        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET", provider_path)
        full_provider_name = response_json["status"]["currentRevision"]

        # Fetch the ClusterRoles for provider system, crossplane, and crossplane-rbac-manager
        provider_cluster_role_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET", provider_role_path.format(full_provider_name=full_provider_name))
        crossplane_cluster_role_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                                    crossplane_role_path)
        crossplane_rbac_manager_cluster_role_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                                                 rbac_manager_role_path)

        # Prepare lists to store any 'configmaps' access rules
        configmap_access_roles = {
            "provider_system": [],
            "crossplane": [],
            "crossplane_rbac_manager": []
        }

        # Define a helper function to filter rules for 'configmaps'
        def extract_configmap_access_rules(cluster_role_json):
            configmap_access_rules = []
            for rule in cluster_role_json.get("rules", []):
                if "configmaps" in rule.get("resources", []):
                    configmap_access_rules.append({
                        "verbs": rule.get("verbs", []),
                        "api_groups": rule.get("apiGroups", []),
                        "resources": ["configmaps"]
                    })
                if "configmaps.coordination.k8s.io" in rule.get("resources", []):
                    configmap_access_rules.append({
                        "verbs": rule.get("verbs", []),
                        "api_groups": rule.get("apiGroups", []),
                        "resources": ["configmaps.coordination.k8s.io"]
                    })
            return configmap_access_rules

        # Populate lists with any 'configmaps' access found in each role
        configmap_access_roles["provider_system"] = extract_configmap_access_rules(provider_cluster_role_json)
        configmap_access_roles["crossplane"] = extract_configmap_access_rules(crossplane_cluster_role_json)
        configmap_access_roles["crossplane_rbac_manager"] = extract_configmap_access_rules(
            crossplane_rbac_manager_cluster_role_json)

        # then
        # Check provider_system for expected access to 'configmaps'
        self.assertEqual(len(configmap_access_roles["provider_system"]), 1,
                         "Expected one configmap access rule in provider_system.")
        self.assertEqual(configmap_access_roles["provider_system"][0]["verbs"], ["*"],
                         "provider_system should have all permissions (*) for configmaps.")
        self.assertIn("", configmap_access_roles["provider_system"][0]["api_groups"],
                      "provider_system should have access to the empty API group for configmaps.")
        self.assertIn("coordination.k8s.io", configmap_access_roles["provider_system"][0]["api_groups"],
                      "provider_system should have access to 'coordination.k8s.io' API group for configmaps.")

        # Check crossplane role for expected access to 'configmaps'
        self.assertEqual(len(configmap_access_roles["crossplane"]), 1,
                         "Expected one configmap access rule in crossplane role.")
        self.assertEqual(configmap_access_roles["crossplane"][0]["verbs"],
                         ['get', 'list', 'create', 'update', 'patch', 'watch', 'delete'],
                         "crossplane role should have limited permissions for configmaps.")
        self.assertEqual(configmap_access_roles["crossplane"][0]["api_groups"], ['', 'coordination.k8s.io'],
                         "crossplane role should have access to both empty and 'coordination.k8s.io' API groups for configmaps.")

        # Verify crossplane_rbac_manager has limited access to configmaps
        self.assertEqual(len(configmap_access_roles["crossplane_rbac_manager"]), 1,
                         "crossplane_rbac_manager role should have access to configmaps.")
        self.assertEqual(configmap_access_roles["crossplane_rbac_manager"][0]["verbs"],
                         ['get', 'list', 'create', 'update', 'patch', 'watch', 'delete'],
                         "crossplane_rbac_manager should have restricted permissions for configmaps.")
        self.assertEqual(configmap_access_roles["crossplane_rbac_manager"][0]["api_groups"],
                         ['', 'coordination.k8s.io'],
                         "crossplane_rbac_manager should have access to both empty and 'coordination.k8s.io' API groups for configmaps.")

    # Test Case 13:
    # Test
    # Objective: Ensure that a Composition is created based on an existing XRD.
    # Preconditions:
    # The XRD required for the Composition is created and available.
    #     Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # A valid XRD YAML file is available.
    # Procedure:
    # Create a Composition based on the existing XRD.
    # Postcondition:
    # Confirm that the Composition is successfully created.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_xr_creating(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        )

        # when
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml"
        )
        response_json = KubernetesResourceManager.send_request_and_get_json_response(
            "GET",
            "/apis/apiextensions.crossplane.io/v1/compositions/xdroplet-composition"
        )

        # then
        self.assertEqual(response_json['metadata']['name'], "xdroplet-composition")
        self.assertEqual(response_json['spec']['compositeTypeRef']['kind'], "XDroplet")
        self.assertEqual(response_json['spec']['compositeTypeRef']['apiVersion'], "compute.crossplane.io/v1alpha1")

        # post condition
        KubernetesResourceManager.delete_cluster_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        )
        KubernetesResourceManager.delete_cluster_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml"
        )

    # Test Case 15: Composition Deletion Test
    # Objective: Confirm that deleting a Composition removes it from the cluster.
    # Preconditions:
    # The XRD for the Composition exists.
    # The Composition has been previously created.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # A valid XRD YAML file is available.
    # Procedure:
    # Delete the Composition.
    # Postcondition:
    # Verify that the Composition is deleted to confirm it no longer exists.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_xr_deleting(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        )
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml"
        )

        # when
        KubernetesResourceManager.delete_cluster_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml"
        )

        remove_response = KubernetesResourceManager.send_request_and_get_response("GET",
                                                                                  "/apis/apiextensions.crossplane.io/v1/compositions/xdroplet-composition")

        # then
        self.assertEqual(remove_response.status_code, 404)

        # post condition
        KubernetesResourceManager.delete_cluster_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        )

    # Test Case 24: RBAC Manager Binding Integrity Test
    # Objective: Ensure that the RBAC Manager cannot modify or delete bindings it does not own.
    # Preconditions:
    # RBAC Manager is configured with limited permissions.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Attempt to modify or delete bindings created by other service accounts using the RBAC Manager's service account.
    # Postcondition:
    # Verify that the RBAC Manager cannot interfere with bindings it does not manage.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_rbac_manager_binding_integrity(self):
        # given
        rbac_manager_role_path = "/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane-rbac-manager"

        # when
        # Fetch the ClusterRole for crossplane-rbac-manager
        crossplane_rbac_manager_cluster_role_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                                                 rbac_manager_role_path)

        # Filter rules for configmaps and clusterrolebindings
        configmap_rules = []
        clusterrolebindings_rules = []

        for rule in crossplane_rbac_manager_cluster_role_json.get("rules", []):
            # Check for configmaps access
            if "configmaps" in rule.get("resources", []):
                configmap_rules.append(rule)
            # Check for clusterrolebindings access
            if "clusterrolebindings" in rule.get("resources", []):
                clusterrolebindings_rules.append(rule)

        # then
        # Verify configmaps access
        self.assertEqual(len(configmap_rules), 1, "crossplane_rbac_manager should have access to configmaps.")
        self.assertEqual(configmap_rules[0]["verbs"], ['get', 'list', 'create', 'update', 'patch', 'watch', 'delete'],
                         "crossplane_rbac_manager should have correct permissions for configmaps.")
        self.assertEqual(configmap_rules[0]["apiGroups"], ['', 'coordination.k8s.io'],
                         "crossplane_rbac_manager should have access to both empty and 'coordination.k8s.io' API groups for configmaps.")

        # Verify clusterrolebindings access
        self.assertEqual(len(clusterrolebindings_rules), 1,
                         "crossplane_rbac_manager should have access to clusterrolebindings.")
        self.assertEqual(clusterrolebindings_rules[0]["verbs"], ['*'],
                         "crossplane_rbac_manager should have full permissions for clusterrolebindings.")
        self.assertEqual(clusterrolebindings_rules[0]["apiGroups"], ['rbac.authorization.k8s.io'],
                         "crossplane_rbac_manager should have access to 'rbac.authorization.k8s.io' API group for clusterrolebindings.")

    # Test Case 22: User Namespace Scope Test
    # Objective: Ensure that users can access claims only within their own namespace.
    # Preconditions:
    # A user with access limited to a specific namespace is created with permission to create claims.
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # Procedure:
    # Attempt to access claims in various namespaces using the limited-scope user.
    # Postcondition:
    # Confirm that the user can access claims only within their assigned namespace.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_user_namespace_scope(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        )
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml"
        )
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/shared_resourses/namespace.yaml"
        )
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/shared_resourses/role.yaml"
        )
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/shared_resourses/role_binding.yaml"
        )

        # when
        role_name = "crossplane-edit"
        namespace = "example-namespace"
        role_api_path = f"/apis/rbac.authorization.k8s.io/v1/namespaces/{namespace}/roles/{role_name}"
        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET", role_api_path)

        # then
        self.assertEqual(response_json['metadata']['name'], role_name, f"Role {role_name} does not exist")
        role_rules = response_json.get('rules', [])
        expected_permissions = [
            {"resource": "events", "verbs": ["get", "list", "watch"], "api_group": ""},
            {"resource": "secrets", "verbs": ["*"], "api_group": ""},
            {"resource": "dropletclaims", "verbs": ["*"], "api_group": "compute.crossplane.io"}
        ]

        def has_all_permissions_for_resource(resource, expected_verbs, api_group):
            return any(
                api_group in rule.get("apiGroups", [])
                and resource in rule.get("resources", [])
                and all(verb in rule.get("verbs", []) for verb in expected_verbs)
                for rule in role_rules
            )

        for permission in expected_permissions:
            resource = permission["resource"]
            expected_verbs = permission["verbs"]
            api_group = permission["api_group"]
            has_permission = has_all_permissions_for_resource(resource, expected_verbs, api_group)
            self.assertTrue(has_permission,
                            f"Role {role_name} does not have the expected permissions for {resource} with verbs {expected_verbs}")

        # post condition
        KubernetesResourceManager.delete_cluster_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        KubernetesResourceManager.delete_cluster_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        KubernetesResourceManager.send_request_and_get_response(
            "DELETE",
            f"/api/v1/namespaces/{namespace}")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/shared_resourses/role.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/shared_resourses/role_binding.yaml")

    # Test Case 3: Provider Managed Resource Creation Test
    # Objective:
    # Ensure that the Kubernetes provider is able to create a Managed Resource and establish a connection with an external cluster.
    # Preconditions:
    # Crossplane is installed and working.
    # Kubernetes provider is installed and operational.
    # Procedure:
    # Configure the provider with necessary settings.
    # Create a Managed Resource, such as a Namespace, via Crossplane.
    # Postcondition:
    # Kubernetes provider configuration should be created.
    # Managed Resource should be created.
    # Kubernetes provider should connect to the 3rd cluster.
    # Managed Resource should be deployed in the 3rd cluster.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_managed_resource_creation(self):

        # when
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_manage_resourse.yaml")

        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                     "apis/compute.do.crossplane.io/v1alpha1/droplets/test-crossplane-droplet")

        # then
        self.assertEqual(response_json['metadata']['name'], "test-crossplane-droplet")
        self.assertEqual(response_json['spec']['forProvider']['region'], "nyc1")
        self.assertEqual(response_json['spec']['forProvider']['size'], "s-1vcpu-1gb")

        conditions = {condition['type']: condition for condition in response_json['status']['conditions']}
        self.assertEqual(conditions.get("Synced", {}).get("status"), "True", "'Synced' condition is not True")
        self.assertEqual(conditions.get("Ready", {}).get("status"), "False", "'Ready' condition is not True")

        # post condition
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_manage_resourse.yaml")

    # Test Case 4: Provider Managed Resource Update Test
    # Objective:
    # Verify that updates to a Managed Resource are correctly applied both within Crossplane and on the external cluster.
    # Preconditions:
    # Crossplane is installed and functioning.
    # Kubernetes provider is installed, configured, and working correctly.
    # A Managed Resource is already created and operational via the Kubernetes provider.
    # Procedure:
    # Update the Managed Resource with new parameters or configurations.
    # Postcondition:
    # Managed Resource should reflect the updated configurations.
    # Resource in the 3rd cluster should be updated accordingly.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_manage_resource_updating(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_provider_config.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_manage_resourse.yaml")

        # when
        updates = {
            "/spec/forProvider/size": "s-2vcpu-2gb",
            "/spec/forProvider/image": "ubuntu-20-04-x64"
        }
        KubernetesResourceManager.update_cluster_resource_parameters(
            f"{manifests_path}/digital_ocean/digital_ocean_manage_resourse.yaml",
            updates)
        response_json = KubernetesResourceManager.send_request_and_get_json_response("GET",
                                                                                     "apis/compute.do.crossplane.io/v1alpha1/droplets/test-crossplane-droplet")

        # then
        self.assertEqual(response_json['metadata']['name'], "test-crossplane-droplet")
        self.assertEqual(response_json['spec']['forProvider']['region'], "nyc1")
        self.assertEqual(response_json['spec']['forProvider']['size'], "s-2vcpu-2gb")

        # post condition
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_provider_config.yaml")
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_manage_resourse.yaml")

    # Test Case 5: Provider Managed Resource Deletion Test
    # Objective:
    # Ensure that deletion of a Managed Resource is correctly propagated, resulting in its removal from both Crossplane and the external cluster.
    # Preconditions:
    # Crossplane is installed and operational.
    # Kubernetes provider is installed, configured, and working correctly.
    # A Managed Resource is created and functioning through the Kubernetes provider.
    # Procedure:
    # Delete the Managed Resource.
    # Postcondition:
    # Managed Resource should be deleted from the NMCCP cluster.
    # Resource in the 3rd cluster should also be deleted.
    # Cleanup:
    # Delete all Crossplane components that were created for this test, including all Crossplane components created by Crossplane itself.
    def test_manage_resource_deleting(self):
        # given
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_provider_config.yaml")
        KubernetesResourceManager.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_manage_resourse.yaml")

        # when
        KubernetesResourceManager.delete_cluster_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_manage_resourse.yaml")

        response = KubernetesResourceManager.send_request_and_get_response("GET",
                                                                           "apis/compute.do.crossplane.io/v1alpha1/droplets/test-crossplane-droplet")

        # then
        self.assertEqual(response.status_code, 404)

        # post condition
        KubernetesResourceManager.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_provider_config.yaml")
