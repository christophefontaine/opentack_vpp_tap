#!/usr/bin/env python

OPENSTACK_CONTROLLER = 'controller'

# AMQP credentials
RABBIT_USER = 'guest'
RABBIT_PASSWORD = 'guest'
RABBIT_SERVER = OPENSTACK_CONTROLLER

# Flask
AGENT_PORT = 8001

# ODL credentials
ODL_SERVER = 'odl'
ODL_PORT = 8181
ODL_USER = 'admin'
ODL_PASSWORD = 'admin'
SFF_LISTENER_NAME = OPENSTACK_CONTROLLER

# Configuration for OVS+ct_mark based Classifier
# Classfier class
CLASSIFIER_MODULE='ovs_conntrack_renderer'
OVS_CLASSIFIER_HOST='ajonc.labo'
OVS_CLASSIFIER_OFFLOADBIT='dpioffload'

# Configuration for DPDK based Service Classifier
# CLASSIFIER_MODULE='sc_renderer'

# Service Classifier UI port
SC_UI_PORT = 8002

