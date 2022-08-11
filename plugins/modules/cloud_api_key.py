#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Rainer Leber <rainerleber@gmail.com> <rainer.leber@sva.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

DOCUMENTATION = '''
---
module: cloud_api_key
author:
  - Ishan Jain (@ishanjainn)
version_added: "0.0.1"
short_description: Manage Grafana Cloud API keys
description:
  - Create and delete Grafana Cloud API keys using Ansible.
requirements: [ "requests >= 1.0.0" ]
options:
  name:
    description:
      - Name of the Grafana Cloud API key.
    type: str
    required: true
  role:
    description:
      - Role to be associated with the CLoud API key.
    type: str
    required: true
    choices: [Admin, Viewer, Editor, MetricsPublisher]
  org_slug:
    description:
      - Name of the Grafana Cloud organization in which Cloud API key will be created
    type: str
    required: true
  existing_cloud_api_key:
    description:
      - CLoud API Key to authenticate with Grafana Cloud.
    type: str
    required : true
  fail_if_already_created:
    description:
      - If set to True, the task will fail if the API key with same name already exists in the Organization.
    type: bool
    default: True
  state:
    description:
      - State for the Grafana CLoud stack.
    type: str
    default: present
    choices: [ present, absent ]
'''

EXAMPLES = '''
- name: Create Grafana Cloud API key
  grafana.grafana.cloud_api_key:
    name: key_name
    role: Admin
    org_slug: "{{ org_slug }}"
    existing_cloud_api_key: "{{ grafana_cloud_api_key }}"
    fail_if_already_created: False
    state: present

- name: Delete Grafana Cloud API key
  grafana.grafana.cloud_api_key:
    name: key_name
    org_slug: "{{ org_slug }}"
    existing_cloud_api_key: "{{ grafana_cloud_api_key }}"
    state: absent
'''

from ansible.module_utils.basic import AnsibleModule
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

__metaclass__ = type


def present_cloud_api_key(module):
    body = {
        'name': module.params['name'],
        'role': module.params['role']
    }

    api_url = 'https://grafana.com/api/orgs/' + module.params['org_slug'] + '/api-keys'

    result = requests.post(api_url, json=body,
                           headers={"Authorization": 'Bearer ' + module.params['existing_cloud_api_key']})

    if result.status_code == 200:
        return False, True, result.json()
    elif result.status_code == 409:
        return module.params['fail_if_already_created'], False, "A Cloud API key with the same name already exists"
    else:
        return True, False, {"status": result.status_code, 'response': result.json()['message']}


def absent_cloud_api_key(module):
    api_url = 'https://grafana.com/api/orgs/' + module.params['org_slug'] + '/api-keys/' + module.params['name']

    result = requests.delete(api_url, headers={"Authorization": 'Bearer ' + module.params['existing_cloud_api_key']})

    if result.status_code == 200:
        return False, True, "Cloud API key is deleted"
    else:
        return True, False, {"status": result.status_code, 'response': result.json()['message']}


def main():
    module_args = dict(
        name=dict(type='str', required=True),
        role=dict(type='str', required=True, choices=['Admin', 'Viewer', 'Editor', 'MetricsPublisher']),
        org_slug=dict(type='str', required=True),
        existing_cloud_api_key=dict(type='str', required=True, no_log=True),
        fail_if_already_created=dict(type='bool', required=False, default='True'),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent'])
    )

    choice_map = {
        "present": present_cloud_api_key,
        "absent": absent_cloud_api_key,
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    is_error, has_changed, result = choice_map.get(
        module.params['state'])(module)

    if not is_error:
        module.exit_json(changed=has_changed, output=result)
    else:
        module.fail_json(msg=result)


if __name__ == '__main__':
    main()
