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
from oslo_service import service
from oslo_service import wsgi
from oslo_context import context
from oslo_config import cfg

from kuryr_rancher import clients
from kuryr_rancher import config
from webob import Request

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class KuryrRancherService:
    def __init__(self, host="0.0.0.0", port="9000", workers=1,
                 use_ssl=False, cert_file=None, ca_file=None):
        self.host = host
        self.port = port
        self.workers = workers
        self.use_ssl = use_ssl
        self.cert_file = cert_file
        self.ca_file = ca_file
        self._actions = {}

    def add_action(self, url_path, action):
        if (url_path.lower() == "default") or (url_path == "/") or (url_path == ""):
            url_path = "default"
        elif not url_path.startswith("/"):
            url_path = "/" + url_path
        self._actions[url_path] = action

    def _app(self, environ, start_response):
        context.RequestContext()
        LOG.debug("start action.")
        request = Request(environ)
        action = self._actions.get(environ['PATH_INFO'])
        if action is None:
            action = self._actions.get("default")
        if action is not None:
            result = action(environ, request.method, request.path_info, request.query_string, request.body)
            try:
                result[1]
            except Exception, e:
                result = ('200 OK', str(result))
            start_response(result[0], [('Content-Type', 'text/plain')])
            return result[1]
        start_response("200 OK", [('Content-type', 'text/html')])
        return "mini service is ok\n"

    def start(self):
        config.init(sys.argv[1:])
        config.setup_logging()
        clients.setup_clients()
        os_vif.initialize()

        self.server = wsgi.Server(CONF,
                                  "kuryr-rancher-controller",
                                  self._app,
                                  host=self.host,
                                  port=self.port,
                                  use_ssl=self.use_ssl)
        launcher = service.ProcessLauncher(CONF)
        launcher.launch_service(self.server, workers=self.workers)
        LOG.debug("launch service (%s:%s)." % (self.host, self.port))
        launcher.wait()
