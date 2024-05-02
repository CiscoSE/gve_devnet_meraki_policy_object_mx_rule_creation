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

import csv
import time

from rich.prompt import Confirm

from config.config import c
from logger.logrr import lm
from meraki_api import meraki_api


def translate_cidr_to_objects(cidr: str) -> str:
    """
    If CIDR string is a Policy Object or Policy Group Object, translate to the compatible format for L3 Rules
    :param cidr: Cidr string (normal cidr, policy object name, policy group object name)
    :return: Compatible cidr format for L3 Rules (if necessary, else return original cidr)
    """
    if cidr in meraki_api.policy_objects_name_to_id:
        # Policy Object
        obj_id = meraki_api.policy_objects_name_to_id[cidr]
        return f"OBJ({obj_id})"
    elif cidr in meraki_api.policy_group_objects_name_to_id:
        # Policy Group Object
        obj_id = meraki_api.policy_group_objects_name_to_id[cidr]
        return f"GRP({obj_id})"
    else:
        # Normal Cidr
        return cidr


def combine_lists(existing_rules: list[dict], new_rules: list[dict]) -> list[dict]:
    """
    Combine two lists of L3 Rules, eliminating duplicates
    :param existing_rules: Existing L3 Rules
    :param new_rules: New L3 Rules
    :return: Combined list of L3 Rules
    """
    key_fields = ['policy', 'protocol', 'srcCidr', 'destCidr', 'srcPort', 'destPort']
    combined_list = []
    seen = set()

    # Helper function to extract key fields into a tuple
    def key_extractor(dic):
        """
        Extract key fields from dictionary into a tuple
        """
        return tuple(dic[key].lower() for key in key_fields)

    # First process existing_rules, which these rules will be kept (ignore default rule)
    for rule in existing_rules:
        key_tuple = key_extractor(rule)

        if key_tuple == ('allow', 'any', 'any', 'any', 'any', 'any'):
            # Skip default rule
            continue

        seen.add(key_tuple)
        combined_list.append(rule)

    # Then process new rules, only adding items not seen in existing_rules
    for rule in new_rules:
        key_tuple = key_extractor(rule)
        if key_tuple not in seen:
            seen.add(key_tuple)
            combined_list.append(rule)

    return combined_list


def main():
    """
    Main Function, create policy objects, policy object groups, apply L3 Outbound Rules to all networks
    :return:
    """
    lm.print_start_panel(app_name=c.APP_NAME)  # Print the start info message to console
    lm.print_config_table(config_instance=c)  # Print the config table

    # Read in CSV of policy objects/groups, create objects and groups
    try:
        with open('policy_objects.csv', mode='r') as file:
            reader = csv.DictReader(file)
            policy_objects = list(reader)
        lm.lnp(f"Read in {len(policy_objects)} Policy Objects", "success")
    except FileNotFoundError as e:
        lm.print_error(f"Policy Object File Not Found: {e}")
        return

    lm.p_panel(f"Create Policy Objects and Policy Groups", title="Step 1")
    for policy_object in policy_objects:
        # Group Name Provided, create or use existing group
        if "_group_name" in policy_object and policy_object["_group_name"] != '':
            # Group doesn't exist, create it!
            if not policy_object["_group_name"] in meraki_api.policy_group_objects_name_to_id:
                group_payload = {"name": policy_object["_group_name"], "category": "NetworkObjectGroup"}
                error, response = meraki_api.create_policy_object_groups(group_payload)

                if error:
                    # Group creation error, skip creating policy object
                    lm.lnp(f"Error Creating Policy Object Group `{policy_object["_group_name"]}`: {error} - {response}",
                           "error")
                    continue
                else:
                    lm.lnp(f"Created Policy Object Group: {response}", "success")

            # Obtain group id, associate new policy object with it
            group_name = policy_object["_group_name"]

            del policy_object["_group_name"]
            policy_object["groupIds"] = [meraki_api.policy_group_objects_name_to_id[group_name]]

        # Create Policy Object
        error, response = meraki_api.create_policy_objects(policy_object)
        if error:
            lm.lnp(f"Error Creating Policy Object `{policy_object['name']}`: {error} - {response}", "error")
        else:
            lm.lnp(f"Created Policy Object: {response}", "success")

    # Read in CSV of L3 Rules
    try:
        with open('l3_outbound_rules.csv', mode='r') as file:
            reader = csv.DictReader(file)
            l3_rules = list(reader)
        lm.lnp(f"Read in {len(l3_rules)} L3 Rules", "success")
    except FileNotFoundError as e:
        lm.print_error(f"L3 Outbound File Not Found: {e}")
        return

    # Translate any src or dst usage of policy object or policy group object into compatible format
    for rule in l3_rules:
        # Source/Dest for Rule
        rule['srcCidr'] = translate_cidr_to_objects(rule['srcCidr'])
        rule['destCidr'] = translate_cidr_to_objects(rule['destCidr'])

    lm.p_panel(f"Create L3 Outbound Rules for All Networks", title="Step 2")

    # Get All Networks
    error, response = meraki_api.get_org_appliance_networks()
    if error:
        lm.lnp(f"Error getting org networks: {error} - {response}", "error")
    else:
        lm.lnp(f"Found the following networks: {[net['name'] for net in response]}", "success")

    time.sleep(1)
    overwrite = Confirm.ask("Overwrite each Networks Existing L3 Rules?", default=False)

    # Apply L3 Rules to each network
    for network in response:
        network_id = network['id']

        if not overwrite:
            # Combine existing rules with rules we added in (eliminate duplicates) if not overwriting
            error, response = meraki_api.get_l3_outbound_rules(network_id)

            if error:
                lm.lnp(f"Error getting existing L3 Rules for `{network['name']}`: {error} - {response}", "error")
                continue

            existing_rules = response['rules']
            l3_rules = combine_lists(existing_rules, l3_rules)

        error, response = meraki_api.update_l3_outbound_rules(network_id, l3_rules)
        if error:
            lm.lnp(f"Error applying L3 Rules to Network `{network['name']}`: {error} - {response}", "error")
        else:
            lm.lnp(f"Successfully applied L3 Rules to Network `{network['name']}`: {response}", "success")


if __name__ == '__main__':
    main()
