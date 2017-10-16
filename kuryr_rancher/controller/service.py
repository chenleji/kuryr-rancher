# Copyright (c) 2016 Mirantis, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
import os_vif

from oslo_log import log as logging
from flask import Flask, jsonify, request, abort
from kuryr_rancher import clients
from kuryr_rancher import config
from kuryr_rancher import objects
from kuryr.lib import constants as kl_const
from kuryr_rancher.controller.handlers import vif as h_vif

app = Flask(__name__)
LOG = logging.getLogger(__name__)

KURYR_RANCHER_LISTEN_ADDR = "0.0.0.0"
KURYR_RANCHER_LISTEN_PORT = 9090

vif_handler = None
neutron_port_map = {}


def port_check(payload):
    if payload is None:
        return False

    if 'name' not in payload.keys() \
            or 'containerID' not in payload.keys() \
            or 'ipAddr' not in payload.keys() \
            or 'macAddr' not in payload.keys() \
            or 'vmIpAddr' not in payload.keys() \
            or 'active' not in payload.keys():
        return False
    return True


@app.route("/", methods=['GET'])
def root():
    logo = {"name": "kuryr-rancher-controller"}
    return jsonify(logo)


@app.route("/health", methods=['GET'])
def health_check():
    payload = {'online': True}
    return jsonify(payload)


@app.route("/v1/kuryr-rancher/port", methods=["POST"])
def create_rancher_port():
    port = request.json
    LOG.info("request %(body)s ", {"body": port})

    if not port_check(port):
        return jsonify({'error': 'invalid request body!'}), 422

    idx = port['containerID']
    if idx in neutron_port_map:
        if neutron_port_map['macAddr'] == port['macAddr'] and \
                        neutron_port_map['ipAddr'] == port['ipAddr']:
            return jsonify({"status": "OK"})
        else:
            port_to_delete = {'deviceOnwer': kl_const.DEVICE_OWNER + ":" + idx}
            vif_handler.on_deleted(port_to_delete)

    vif_handler.on_added(port)
    if not vif_handler.on_present(port):
        return jsonify({"error": "create neutron port failed!"}), 500

    neutron_port_map[idx] = {
        'ipAddr': port['ipAddr'],
        'macAddr': port['macAddr'],
    }

    return jsonify({"status": "OK"})


@app.route("/v1/kuryr-rancher/port/<idx>", methods=["DELETE", "GET"])
def get_or_delete_rancher_port(idx):
    port = {'deviceOnwer': kl_const.DEVICE_OWNER + ":" + idx}

    if request.method == 'GET':
        LOG.info("port %(port)s", {"port": port})
        return jsonify({"status": "OK"})
    else:
        vif_handler.on_deleted(port)

        try:
            neutron_port_map.pop(idx)
        except Exception as ex:
            LOG.error("can't find neutron port in neutron_port_map cache,  %(exception)s", {'exception': ex})

        return jsonify({"status": "OK"})


def sync_neutron_port_map():
    neutron = clients.get_neutron_client()
    try:
        neutron_ports = neutron.list_ports().get('ports')
    except Exception as ex:
        LOG.error("Unable to sync ports with neutron, %(exception)s", {'exception': ex})
        return

    for port in neutron_ports:
        if 'device_owner' in port:
            device_owner = port['device_owner']
            if device_owner.startswith(kl_const.DEVICE_OWNER):
                # get container id
                start_idx = device_owner.rindex(":") + 1
                container_id = device_owner[start_idx:]

                # get ip address
                container_ips = set(entry['ip_address'] for entry in port['fixed_ips'])
                container_ip = container_ips.pop()

                # get mac address
                container_mac = port['mac_address']

                neutron_port_map[container_id] = {
                    'ipAddr': container_ip,
                    'macAddr': container_mac,
                }


def start():
    config.init(sys.argv[1:])
    config.setup_logging()
    clients.setup_clients()
    os_vif.initialize()

    objects.register_locally_defined_vifs()
    sync_neutron_port_map()

    global vif_handler
    vif_handler = h_vif.VIFHandler()

    app.run(host=KURYR_RANCHER_LISTEN_ADDR, port=KURYR_RANCHER_LISTEN_PORT, debug=True)
