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
from flask import Flask, jsonify, request
from kuryr_rancher import clients
from kuryr_rancher import config
from kuryr_rancher import objects
from kuryr_rancher.controller.handlers import vif as h_vif

app = Flask(__name__)
LOG = logging.getLogger(__name__)

KURYR_RANCHER_LISTEN_ADDR = "0.0.0.0"
KURYR_RANCHER_LISTEN_PORT = 8080


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
    LOG.info("invoke %(method)s | %(url)s ", {"method": request.method, "url": request.url})
    LOG.info("request %(body)s ", {"body": request.json})

    obj = request.json
    # TODO translate obj
    vif_handler.on_added(obj)
    vif_handler.on_present(obj)


@app.route("/v1/kuryr-rancher/port/<port_id>", methods=["DELETE", "GET"])
def get_or_delete_rancher_port(port_id):
    LOG.info("invoke %(method)s | %(url)s ", {"method": request.method, "url": request.url})

    if request.method == 'GET':
        LOG.info("port %(port)s", {"port": port_id})
        return jsonify({"status": "OK"})

    else:
        obj = request.json
        # TODO translate obj
        vif_handler.on_deleted(obj)


def start():
    config.init(sys.argv[1:])
    config.setup_logging()
    clients.setup_clients()
    os_vif.initialize()

    objects.register_locally_defined_vifs()

    global vif_handler
    vif_handler = h_vif.VIFHandler()

    app.run(host=KURYR_RANCHER_LISTEN_ADDR, port=KURYR_RANCHER_LISTEN_PORT, debug=True)
