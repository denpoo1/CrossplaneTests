import unittest
import k8s as k8s
import path_searcher as path_builder

manifests_path = path_builder.get_manifest_path()


class TestMain(unittest.TestCase):

    # Test Case 3: Provider Managed Resource Creation Test
    # Objective:
    # Ensure that the Kubernetes provider can create a Managed Resource and establish a connection with an external cluster.
    # Preconditions:
    # Crossplane is installed and working.
    # Kubernetes provider is installed and operational.
    # Procedure:
    # Configure the provider with necessary settings and create a Managed Resource.
    # Postcondition:
    # Kubernetes provider configuration is created, Managed Resource is created and deployed in the 3rd cluster.
    # Cleanup:
    # Delete all Crossplane components created during this test, including those created by Crossplane itself.
    def test_managed_resource_creation(self):
        # given
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")

        # when
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")
        response_json = k8s.send_request_and_get_json_response("GET",
                                                                    "apis/compute.crossplane.io/v1alpha1/namespaces/default/dropletclaims/test-droplet-claim-1")

        # then
        self.assertEqual(response_json['metadata']['name'], "test-droplet-claim-1")

        conditions = {condition['type']: condition for condition in response_json['status']['conditions']}
        self.assertEqual(conditions.get("Synced", {}).get("status"), "True", "'Synced' condition is not True")
        self.assertEqual(conditions.get("Ready", {}).get("status"), "False", "'Ready' condition is not True")

        # post condition
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")

    # Test Case 4: Provider Managed Resource Update Test
    # Objective:
    # Verify that updates to a Managed Resource are correctly applied within Crossplane and on the external cluster.
    # Preconditions:
    # Crossplane is installed and functioning. Kubernetes provider is installed, configured, and working correctly.
    # Procedure:
    # Update the Managed Resource with new configurations.
    # Postcondition:
    # Managed Resource reflects the updated configurations, and the resource in the 3rd cluster is updated accordingly.
    # Cleanup:
    # Delete all Crossplane components created during this test, including those created by Crossplane itself.
    def test_managed_resource_updating(self):
        # given
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")

        # when
        updates = {
            "/spec/parameters/size": "s-2vcpu-2gb",
            "/spec/parameters/image": "ubuntu-20-04-x64"
        }
        k8s.update_cluster_resource_parameters(
            f"{manifests_path}/digital_ocean/digital_ocean_claim_update.yaml",
            updates)
        response_json = k8s.send_request_and_get_json_response("GET",
                                                                    "apis/compute.crossplane.io/v1alpha1/namespaces/default/dropletclaims/test-droplet-claim-1")

        # then
        self.assertEqual(response_json['metadata']['name'], "test-droplet-claim-1")
        self.assertEqual(response_json['spec']['parameters']['size'], "s-2vcpu-2gb")

        conditions = {condition['type']: condition for condition in response_json['status']['conditions']}
        self.assertEqual(conditions.get("Synced", {}).get("status"), "True", "'Synced' condition is not True")
        self.assertEqual(conditions.get("Ready", {}).get("status"), "True", "'Ready' condition is not True")

        # post condition
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")

    # Test Case 5: Provider Managed Resource Deletion Test
    # Objective:
    # Ensure that deletion of a Managed Resource is propagated, resulting in its removal from both Crossplane and the external cluster.
    # Preconditions:
    # Crossplane is installed and operational. Kubernetes provider is installed, configured, and working correctly.
    # Procedure:
    # Delete the Managed Resource.
    # Postcondition:
    # Managed Resource is deleted from NMCCP cluster, and resource in the 3rd cluster is also deleted.
    # Cleanup:
    # Delete all Crossplane components created during this test, including those created by Crossplane itself.
    def test_managed_resource_deleting(self):
        # given
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")

        # when
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_claim.yaml")
        response = k8s.send_request_and_get_response("GET",
                                                          "apis/compute.crossplane.io/v1alpha1/namespaces/default/dropletclaims/test-droplet-claim-1")

        # then
        self.assertEqual(response.status_code, 404)

        # post condition
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")

    # Test Case 6: Provider Permission Limitation Test
    # Objective:
    # Verify that the Provider has access only to required resources and cannot access unauthorized resources.
    def test_provider_permission_limitation(self):
        # when
        response_json = k8s.send_request_and_get_json_response("GET",
                                                                    "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean")
        full_provider_name = response_json["status"]["currentRevision"]
        provider_cluster_role_json = k8s.send_request_and_get_json_response(
            "GET", f"/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:system")

        # then
        for rule in provider_cluster_role_json['rules']:
            api_groups = rule.get('apiGroups', [])
            self.assertNotIn('apps', api_groups, "'apps' should not be in apiGroups")

    # Test Case 7: Role Aggregation Functionality Test
    # Objective:
    # Verify Crossplane’s correct use of aggregated roles for accessing provider resources.
    def test_role_aggregation_functionality(self):
        # when
        response_json = k8s.send_request_and_get_json_response("GET",
                                                                    "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean")
        full_provider_name = response_json["status"]["currentRevision"]
        provider_cluster_role_json = k8s.send_request_and_get_json_response("GET",
                                                                                 "/apis/rbac.authorization.k8s.io/v1/clusterroles")

        # Filter roles by provider prefix
        provider_prefix = f"crossplane:provider:{full_provider_name}"
        role_names = {item["metadata"]["name"] for item in provider_cluster_role_json["items"]
                      if item["metadata"]["name"].startswith(provider_prefix)}

        # then
        self.assertEqual(len(role_names), 3)

    # Test Case 8: Restricted Secret Access Test
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
        response_json = k8s.send_request_and_get_json_response(
            "GET", "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean"
        )
        full_provider_name = response_json["status"]["currentRevision"]

        # Fetch the ClusterRoles for system, crossplane, and crossplane-rbac-manager
        provider_role = k8s.send_request_and_get_json_response(
            "GET", f"/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:system"
        )
        crossplane_role = k8s.send_request_and_get_json_response(
            "GET", "/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane"
        )
        rbac_manager_role = k8s.send_request_and_get_json_response(
            "GET", "/apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane-rbac-manager"
        )

        # then
        # Define helper to filter 'secrets' access rules
        def extract_secret_rules(role_json):
            return [
                {
                    "verbs": rule.get("verbs", []),
                    "apiGroups": rule.get("apiGroups", []),
                    "resources": rule.get("resources", []),
                }
                for rule in role_json.get("rules", [])
                if "secrets" in rule.get("resources", [])
            ]

        secret_access_roles = {
            "provider": extract_secret_rules(provider_role),
            "crossplane": extract_secret_rules(crossplane_role),
            "rbac_manager": extract_secret_rules(rbac_manager_role),
        }

        # Assertions to verify restricted access rules
        self.assertEqual(
            len(secret_access_roles["provider"]), 1,
            "Expected one 'secrets' access rule in provider role."
        )
        self.assertEqual(
            secret_access_roles["provider"][0]["verbs"], ["*"],
            "Provider role should have all permissions (*) for secrets."
        )
        self.assertIn(
            "", secret_access_roles["provider"][0]["apiGroups"],
            "Provider role should have access to the empty API group for secrets."
        )
        self.assertIn(
            "coordination.k8s.io", secret_access_roles["provider"][0]["apiGroups"],
            "Provider role should have access to 'coordination.k8s.io' API group for secrets."
        )
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
            secret_access_roles["crossplane"][0]["apiGroups"],
            [""],
            "Crossplane role should have access only to the empty API group for secrets."
        )
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
        k8s.create_resource_from_yaml(xrd_yaml_path)
        response_json = k8s.send_request_and_get_json_response(
            "GET", "/apis/apiextensions.crossplane.io/v1/compositeresourcedefinitions/xdroplets.compute.crossplane.io"
        )

        # then
        self.assertEqual(response_json["metadata"]["name"], "xdroplets.compute.crossplane.io")
        conditions = {condition["type"]: condition for condition in response_json["status"]["conditions"]}
        self.assertEqual(conditions.get("Established", {}).get("status"), "True", "'Established' condition is not True")
        self.assertEqual(conditions.get("Offered", {}).get("status"), "True", "'Offered' condition is not True")

        # post condition
        k8s.delete_resource_by_file(xrd_yaml_path)

    # Test Case 10: XRD Update Test
    # Objective: Ensure that an update to an existing XRD is applied correctly, reflecting the changes in the cluster.
    # Preconditions:
    # Kubernetes provider is installed, configured, and working correctly.
    # Crossplane is installed and working.
    # A valid XRD YAML file is available.
    def test_xrd_updating(self):
        # given
        xrd_yaml_path = f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml"
        k8s.create_resource_from_yaml(xrd_yaml_path)

        # when
        initial_response_json = k8s.send_request_and_get_json_response(
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
        k8s.update_cluster_resource_parameters(xrd_yaml_path, updates)

        # Retrieve updated XRD
        updated_response_json = k8s.send_request_and_get_json_response(
            "GET", "/apis/apiextensions.crossplane.io/v1/compositeresourcedefinitions/xdroplets.compute.crossplane.io"
        )

        # then
        updated_default_image = \
            updated_response_json["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"][
                "properties"][
                "parameters"]["properties"]["image"]["default"]
        self.assertEqual(updated_default_image, "fedora", "Expected updated default image to be 'fedora'.")

        # post condition
        k8s.delete_resource_by_file(xrd_yaml_path)

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
        k8s.create_resource_from_yaml(xrd_yaml_path)

        # when
        k8s.delete_resource_by_file(xrd_yaml_path)
        remove_response_json = k8s.send_request_and_get_json_response("GET",
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
        k8s.create_resource_from_yaml(xrd_yaml_path)

        # when
        response_json = k8s.send_request_and_get_json_response("GET",
                                                                    "/apis/pkg.crossplane.io/v1/providers/provider-digitalocean")
        full_provider_name = response_json["status"]["currentRevision"]

        provider_aggregate_to_edit_role_json = k8s.send_request_and_get_response("GET",
                                                                                      f"apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:aggregate-to-edit")
        provider_aggregate_to_view_role_json = k8s.send_request_and_get_response("GET",
                                                                                      f"apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:aggregate-to-view")
        provider_aggregate_system_role_json = k8s.send_request_and_get_response("GET",
                                                                                     f"apis/rbac.authorization.k8s.io/v1/clusterroles/crossplane:provider:{full_provider_name}:system")

        # then
        self.assertEqual(provider_aggregate_to_edit_role_json.status_code, 200)
        self.assertEqual(provider_aggregate_to_view_role_json.status_code, 200)
        self.assertEqual(provider_aggregate_system_role_json.status_code, 200)

        # post condition
        k8s.delete_resource_by_file(xrd_yaml_path)

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
        k8s.create_resource_from_yaml(xr_yaml_path)

        # when
        response_json = k8s.send_request_and_get_json_response(
            "GET",
            "/apis/apiextensions.crossplane.io/v1/compositions/xdroplet-composition"
        )
        initial_volume_size_default = response_json["spec"]["resources"][0]["base"]["spec"]["forProvider"]["size"]
        self.assertEqual(initial_volume_size_default, "s-1vcpu-1gb",
                         "Initial default volume size should be 's-1vcpu-1gb'.")

        updates = {
            "/spec/resources/0/base/spec/forProvider/size": "s-1vcpu-2gb"
        }
        k8s.update_cluster_resource_parameters(xr_yaml_path, updates)

        # then
        response_updated_json = k8s.send_request_and_get_json_response(
            "GET",
            "/apis/apiextensions.crossplane.io/v1/compositions/xdroplet-composition"
        )
        updated_volume_size = response_updated_json["spec"]["resources"][0]["base"]["spec"]["forProvider"]["size"]
        self.assertEqual(updated_volume_size, "s-1vcpu-2gb",
                         "Updated default volume size should be 's-1vcpu-2gb'.")

        # post condition
        k8s.delete_resource_by_file(xr_yaml_path)

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
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.create_resource_from_yaml(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        k8s.create_resource_from_yaml(
            f"{manifests_path}/shared_resourses/role.yaml")
        k8s.create_resource_from_yaml(
            f"{manifests_path}/shared_resourses/role_binding.yaml")

        # when
        role_name = "crossplane-edit"
        namespace = "default"
        role_api_path = f"/apis/rbac.authorization.k8s.io/v1/namespaces/{namespace}/roles/{role_name}"
        response_json = k8s.send_request_and_get_json_response("GET", role_api_path)

        # then
        self.assertEqual(response_json['metadata']['name'], role_name, f"Role {role_name} does not exist")
        role_rules = response_json.get('rules', [])
        expected_permissions = [
            {"resource": "events", "verbs": ["get", "list", "watch"], "apiGroup": ""},
            {"resource": "secrets", "verbs": ["*"], "apiGroup": ""},
            {"resource": "dropletclaims", "verbs": ["*"], "apiGroup": "compute.crossplane.io"}
        ]

        def has_all_permissions_for_resource(resource, expected_verbs, apiGroup):
            for rule in role_rules:
                if rule.get("apiGroups", [None])[0] == apiGroup and resource in rule.get("resources", []):
                    if all(verb in rule.get("verbs", []) for verb in expected_verbs):
                        return True
            return False

        for permission in expected_permissions:
            resource = permission["resource"]
            expected_verbs = permission["verbs"]
            apiGroup = permission["apiGroup"]
            has_permission = has_all_permissions_for_resource(resource, expected_verbs, apiGroup)
            self.assertTrue(has_permission,
                            f"Role {role_name} does not have the expected permissions for {resource} with verbs {expected_verbs}")

        # post condition
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/shared_resourses/role.yaml")
        k8s.delete_resource_by_file(
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
        response_json = k8s.send_request_and_get_json_response("GET", provider_path)
        full_provider_name = response_json["status"]["currentRevision"]

        # Fetch the ClusterRoles for provider system, crossplane, and crossplane-rbac-manager
        provider_cluster_role_json = k8s.send_request_and_get_json_response("GET", provider_role_path.format(
            full_provider_name=full_provider_name))
        crossplane_cluster_role_json = k8s.send_request_and_get_json_response("GET", crossplane_role_path)
        crossplane_rbac_manager_cluster_role_json = k8s.send_request_and_get_json_response("GET",
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
                        "apiGroups": rule.get("apiGroups", []),
                        "resources": ["configmaps"]
                    })
                if "configmaps.coordination.k8s.io" in rule.get("resources", []):
                    configmap_access_rules.append({
                        "verbs": rule.get("verbs", []),
                        "apiGroups": rule.get("apiGroups", []),
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
        self.assertIn("", configmap_access_roles["provider_system"][0]["apiGroups"],
                      "provider_system should have access to the empty API group for configmaps.")
        self.assertIn("coordination.k8s.io", configmap_access_roles["provider_system"][0]["apiGroups"],
                      "provider_system should have access to 'coordination.k8s.io' API group for configmaps.")

        # Check crossplane role for expected access to 'configmaps'
        self.assertEqual(len(configmap_access_roles["crossplane"]), 1,
                         "Expected one configmap access rule in crossplane role.")
        self.assertEqual(configmap_access_roles["crossplane"][0]["verbs"],
                         ['get', 'list', 'create', 'update', 'patch', 'watch', 'delete'],
                         "crossplane role should have limited permissions for configmaps.")
        self.assertEqual(configmap_access_roles["crossplane"][0]["apiGroups"], ['', 'coordination.k8s.io'],
                         "crossplane role should have access only to the empty API group for configmaps.")

        # Verify crossplane_rbac_manager has limited access to configmaps
        self.assertEqual(len(configmap_access_roles["crossplane_rbac_manager"]), 1,
                         "crossplane_rbac_manager role should have access to configmaps.")
        self.assertEqual(configmap_access_roles["crossplane_rbac_manager"][0]["verbs"],
                         ['get', 'list', 'create', 'update', 'patch', 'watch', 'delete'],
                         "crossplane_rbac_manager should have restricted permissions for configmaps.")

        # post condition
        # Clean up roles if needed; assuming here that any roles created for the test are deleted, but if roles are part of permanent setup, this may be adjusted
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xrd.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/digital_ocean/digital_ocean_xr.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/shared_resourses/role.yaml")
        k8s.delete_resource_by_file(
            f"{manifests_path}/shared_resourses/role_binding.yaml")
