#!/bin/bash

cat > /etc/kuryr.conf << EOF
[DEFAULT]
use_stderr = true
bindir = {path_to_env}/libexec/kuryr

[kubernetes]
api_root = http://{ip_of_kubernetes_apiserver}:8080

[neutron]
auth_url = ${OPENSTACK_AUTH_URL}
username = ${OPENSTACK_USER_NAME}
user_domain_name = ${OPENSTACK_USER_DOMAIN_NAME}
password = ${OPENSTACK_PASSWORD}
project_name = ${NEUTRON_PROJECT_NAME}
project_domain_name = ${NEUTRON_PROJECT_DOMAIN_NAME}
auth_type = password

[pod_vif_nested]
worker_nodes_subnet = ${RANCHER_NEUTRON_WORKER_NODE_SUBNET}

[neutron_defaults]
ovs_bridge = br-int
pod_security_groups = ${RANCHER_NEUTRON_SECURITY_GROUPS}
pod_subnet = ${RANCHER_NEUTRON_SUBNET}
project = ${RANCHER_NEUTRON_PROJECT}
service_subnet = {id_of_subnet_for_rancher_services}
EOF

sleep 2

/usr/bin/kuryr-rancher-controller --config-dir /etc/kuryr &
wait $!