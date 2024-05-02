#!/usr/bin/env python3
"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Trevor Maco <tmaco@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

from typing import ClassVar, Optional

import meraki

from config.config import c


class MERAKI_API(object):
    """
    Meraki API Class, includes various methods to interact with Meraki API
    """
    _instance: ClassVar[Optional['MERAKI_API']] = None

    def __init__(self):
        """
        Initialize the Meraki class: dashboard sdk instance
        """
        self.org_id = c.ORG_ID
        self.retry_429_count = 25
        self.dashboard = meraki.DashboardAPI(api_key=c.MERAKI_API_KEY, suppress_logging=True,
                                             caller=c.APP_NAME, maximum_retries=self.retry_429_count)

        # Get Current Policy Objects, create name to id mapping
        self._policy_objects_name_to_id = {}
        policy_objects = self.dashboard.organizations.getOrganizationPolicyObjects(self.org_id, total_pages='all')
        for policy_object in policy_objects:
            self._policy_objects_name_to_id[policy_object['name']] = policy_object['id']

        # Get Current Policy Objects Groups, create name to id mapping
        self._policy_group_objects_name_to_id = {}
        policy_object_groups = self.dashboard.organizations.getOrganizationPolicyObjectsGroups(self.org_id,
                                                                                               total_pages='all')
        for policy_object_group in policy_object_groups:
            self._policy_group_objects_name_to_id[policy_object_group['name']] = policy_object_group['id']

    @classmethod
    def get_instance(cls):
        """
        Get Singleton instance of Meraki Class
        :return: Singleton instance of Meraki Class
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def policy_objects_name_to_id(self):
        """
        Get the policy_objects_name_to_id mapping
        :return: The policy_objects_name_to_id dictionary
        """
        return self._policy_objects_name_to_id

    @property
    def policy_group_objects_name_to_id(self):
        """
        Get the policy_group_objects_name_to_id mapping
        :return: The policy_group_objects_name_to_id dictionary
        """
        return self._policy_group_objects_name_to_id

    def get_org_appliance_networks(self) -> tuple[str | None, list | str]:
        """
        Getr Org Appliance Networks (or subset), return response or (error code, error message)
        https://developer.cisco.com/meraki/api-v1/get-organization-networks/
        :return: Error Code (if relevant), Response (or Error Message)
        """
        try:
            response = self.dashboard.organizations.getOrganizationNetworks(self.org_id)
            if len(c.NETWORK_NAMES) > 0:
                appliance_networks = [network for network in response if
                                      'appliance' in network['productTypes'] and network['name'] in c.NETWORK_NAMES]
            else:
                appliance_networks = [network for network in response if 'appliance' in network['productTypes']]
            return None, appliance_networks
        except meraki.APIError as e:
            return e.status, str(e)
        except Exception as e:
            # SDK Error
            return "500", str(e)

    def create_policy_objects(self, policy_object_config: dict) -> tuple[str | None, dict | str]:
        """
        Create Network Policy Object, return response or (error code, error message)
        https://developer.cisco.com/meraki/api-v1/create-organization-policy-object/
        :param policy_object_config: Create Policy Object payload
        :return: Error Code (if relevant), Response (or Error Message)
        """
        try:
            response = self.dashboard.organizations.createOrganizationPolicyObject(self.org_id, **policy_object_config)
            self._policy_objects_name_to_id[policy_object_config['name']] = response['id']
            return None, response
        except meraki.APIError as e:
            return e.status, str(e)
        except Exception as e:
            # SDK Error
            return "500", str(e)

    def create_policy_object_groups(self, policy_object_group_config: dict) -> tuple[str | None, dict | str]:
        """
        Create Network Policy Object, return response or (error code, error message)
        https://developer.cisco.com/meraki/api-v1/create-organization-policy-objects-group/
        :param policy_object_group_config: Create Policy Object Group payload
        :return: Error Code (if relevant), Response (or Error Message)
        """
        try:
            response = self.dashboard.organizations.createOrganizationPolicyObjectsGroup(self.org_id,
                                                                                         **policy_object_group_config)
            self._policy_group_objects_name_to_id[policy_object_group_config['name']] = response['id']
            return None, response
        except meraki.APIError as e:
            return e.status, str(e)
        except Exception as e:
            # SDK Error
            return "500", str(e)

    def get_l3_outbound_rules(self, network_id: str) -> tuple[str | None, dict | str]:
        """
        Getr Existing L3 Outbound Rules, return response or (error code, error message)
        https://developer.cisco.com/meraki/api-v1/get-network-appliance-firewall-l-3-firewall-rules/
        :param network_id: Network ID
        :return: Error Code (if relevant), Response (or Error Message)
        """
        try:
            response = self.dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules(network_id)
            return None, response
        except meraki.APIError as e:
            return e.status, str(e)
        except Exception as e:
            # SDK Error
            return "500", str(e)

    def update_l3_outbound_rules(self, network_id: str, l3_rules_list: list) -> tuple[str | None, dict | str]:
        """
        Update L3 Rules, return response or (error code, error message)
        https://developer.cisco.com/meraki/api-v1/update-network-appliance-firewall-l-3-firewall-rules/
        :param network_id: Network ID
        :param l3_rules_list: List of L3 Rules
        :return: Error Code (if relevant), Response (or Error Message)
        """
        try:
            response = self.dashboard.appliance.updateNetworkApplianceFirewallL3FirewallRules(networkId=network_id,
                                                                                              rules=l3_rules_list)
            return None, response
        except meraki.APIError as e:
            return e.status, str(e)
        except Exception as e:
            # SDK Error
            return "500", str(e)


meraki_api = MERAKI_API.get_instance()  # Singleton instance of MERAKI_API
