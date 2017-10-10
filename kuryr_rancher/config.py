# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os
import sys

from kuryr.lib._i18n import _
from kuryr.lib import config as lib_config
from oslo_config import cfg
from oslo_log import log as logging

from kuryr_rancher import version

LOG = logging.getLogger(__name__)

kuryr_rancher_opts = [
    cfg.StrOpt('pybasedir',
               help=_('Directory where Kuryr-rancher python module is '
                      'installed.'),
               default=os.path.abspath(
                   os.path.join(os.path.dirname(__file__),
                                '../../'))),
]

rancher_opts = [
    cfg.StrOpt('pod_project_driver',
               help=_("The driver to determine OpenStack "
                      "project for pod ports"),
               default='default'),
    cfg.StrOpt('service_project_driver',
               help=_("The driver to determine OpenStack "
                      "project for services"),
               default='default'),
    cfg.StrOpt('pod_subnets_driver',
               help=_("The driver to determine Neutron "
                      "subnets for pod ports"),
               default='default'),
    cfg.StrOpt('service_subnets_driver',
               help=_("The driver to determine Neutron "
                      "subnets for services"),
               default='default'),
    cfg.StrOpt('pod_security_groups_driver',
               help=_("The driver to determine Neutron "
                      "security groups for pods"),
               default='default'),
    cfg.StrOpt('service_security_groups_driver',
               help=_("The driver to determine Neutron "
                      "security groups for services"),
               default='default'),
    cfg.StrOpt('pod_vif_driver',
               help=_("The driver that provides VIFs for Kubernetes Pods."),
               default='neutron-vif'),
    cfg.StrOpt('endpoints_lbaas_driver',
               help=_("The driver that provides LoadBalancers for "
                      "Kubernetes Endpoints"),
               default='lbaasv2'),
    cfg.StrOpt('vif_pool_driver',
               help=_("The driver that manages VIFs pools for "
                      "Kubernetes Pods."),
               default='noop'),
]

neutron_defaults = [
    cfg.StrOpt('project',
               help=_("Default OpenStack project ID for "
                      "Kubernetes resources")),
    cfg.StrOpt('pod_subnet',
               help=_("Default Neutron subnet ID for Kubernetes pods")),
    cfg.ListOpt('pod_security_groups',
                help=_("Default Neutron security groups' IDs "
                       "for Kubernetes pods")),
    cfg.StrOpt('ovs_bridge',
               help=_("Default OpenVSwitch integration bridge"),
               sample_default="br-int"),
    cfg.StrOpt('service_subnet',
               help=_("Default Neutron subnet ID for Kubernetes services")),
    cfg.StrOpt('external_svc_subnet',
               help=_("Default external subnet for Kubernetes services")),
]

CONF = cfg.CONF
CONF.register_opts(kuryr_rancher_opts)
CONF.register_opts(rancher_opts, group='rancher')
CONF.register_opts(neutron_defaults, group='neutron_defaults')

CONF.register_opts(lib_config.core_opts)
CONF.register_opts(lib_config.binding_opts, 'binding')
lib_config.register_neutron_opts(CONF)

logging.register_options(CONF)


def init(args, **kwargs):
    version_rancher = version.version_info.version_string()
    CONF(args=args, project='kuryr-rancher', version=version_rancher, **kwargs)


def setup_logging():

    logging.setup(CONF, 'kuryr-rancher')
    logging.set_defaults(default_log_levels=logging.get_default_log_levels())
    version_rancher = version.version_info.version_string()
    LOG.info("Logging enabled!")
    LOG.info("%(prog)s version %(version)s",
             {'prog': sys.argv[0], 'version': version_rancher})
