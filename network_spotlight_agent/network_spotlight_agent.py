#!/usr/bin/env python
# Copyright  Qosmos 2000-2015 - All rights reserved

import platform
import logging
from rabbit_listener import run_listener, MQHooks
LOG = logging.getLogger(__name__)
logging.basicConfig(level=20)


class NetworkSpotlightAgent():
    def _RPC_change_instance_metadata(self, args):
        instance_args = args['instance']['nova_object.data']
        LOG.info ("****************************************************")
        LOG.info ('_RPC_change_instance_metadata')
        LOG.info (instance_args['uuid'])
        LOG.info (instance_args['project_id'])
        LOG.info (instance_args['metadata'])
        LOG.info ("****************************************************")
        if 'nsa' in instance_args['metadata'] and self._vm_is_local(instance_args['host']):
            if instance_args['metadata']['nsa'] == 'True':
                self._enable_spotlight(instance_args['project_id'],
                                       instance_args['uuid'])
            else:
                self._disable_spotlight(instance_args['project_id'],
                                       instance_args['uuid'])

    def _vm_is_local(self, hostname):
        LOG.info('_vm_is_local: ' + hostname)
        return hostname == platform.node()

    def _enable_spotlight(self, tenant_id, instance_id):
        LOG.info('_enable_spotlight')
        return

    def _disable_spotlight(self, tenant_id, instance_id):
        LOG.info('_disable_spotlight')
        return


def main():
    MQHooks.append(NetworkSpotlightAgent())
    run_listener("nova", "compute.#")
    

if __name__ == '__main__':
    main()
