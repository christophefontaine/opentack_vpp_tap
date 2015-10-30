#!/usr/bin/env python
# Copyright  Qosmos 2000-2015 - All rights reserved

import platform
import logging
import json
import subprocess
import signal
from rabbit_listener import run_listener, MQHooks
LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

LICENCE_FILE = 'Q1500085-20150626.bin'


class NetworkSpotlightAgent():
    def __init__(self):
        self.children = {}

    def _RPC_change_instance_metadata(self, args):
        instance_args = args['instance']['nova_object.data']
        j = instance_args['info_cache']['nova_object.data']['network_info']
        network_info = json.loads(j)
        dev_names = [n['devname'] for n in network_info]
        LOG.info("****************************************************")
        LOG.info('_RPC_change_instance_metadata')
        LOG.info(instance_args['uuid'])
        LOG.info(instance_args['project_id'])
        LOG.info(instance_args['metadata'])
        LOG.info(str(dev_names))
        LOG.info("****************************************************")
        if 'nsa' in instance_args['metadata'] and self._vm_is_local(instance_args['host']):
            if instance_args['metadata']['nsa'] == 'True':
                self._enable_spotlight(instance_args['project_id'],
                                       instance_args['user_id'],
                                       instance_args['uuid'],
                                       dev_names)
            else:
                self._disable_spotlight(instance_args['project_id'],
                                        instance_args['user_id'],
                                        instance_args['uuid'],
                                        dev_names)

    # We can NOT use build_and_run as the
    # network info blob is not yet populated
    # use instead 'external_instance_event, and filter on vm_state
    def _RPC_external_instance_event(self, args):
      try:
        for instance in args['instances']:
            instance_args = instance['nova_object.data']
            if instance_args['vm_state'] == 'building':
                self._RPC_start_instance(args)
      except:
        pass  # TODO

    def _RPC_terminate_instance(self, args):
        self._RPC_stop_instance(args)

    def _RPC_pause_instance(self, args):
        self._RPC_stop_instance(args)

    def _RPC_unpause_instance(self, args):
        self._RPC_start_instance(args)

    def _RPC_suspend_instance(self, args):
        self._RPC_stop_instance(args)

    def _RPC_resume_instance(self, args):
        self._RPC_start_instance(args)

    def _RPC_start_instance(self, args):
        instance_args = args['instance']['nova_object.data']
        j = instance_args['info_cache']['nova_object.data']['network_info']
        network_info = json.loads(j)
        dev_names = [n['devname'] for n in network_info]
        if 'nsa' in instance_args['metadata'] and self._vm_is_local(instance_args['host']):
            if instance_args['metadata']['nsa'] == 'True':
                self._enable_spotlight(instance_args['project_id'],
                                       instance_args['user_id'],
                                       instance_args['uuid'],
                                       dev_names)

    def _RPC_stop_instance(self, args):
        instance_args = args['instance']['nova_object.data']
        j = instance_args['info_cache']['nova_object.data']['network_info']
        network_info = json.loads(j)
        dev_names = [n['devname'] for n in network_info]
        if 'nsa' in instance_args['metadata'] and self._vm_is_local(instance_args['host']):
            if instance_args['metadata']['nsa'] == 'True':
                self._disable_spotlight(instance_args['project_id'],
                                        instance_args['user_id'],
                                        instance_args['uuid'],
                                        dev_names)

    def _vm_is_local(self, hostname):
        LOG.info('_vm_is_local: ' + hostname)
        return hostname == platform.node()

    def _enable_spotlight(self, tenant_id, user_id, instance_id, devices):
        LOG.info('_enable_spotlight %s %s %s', tenant_id, instance_id, str(devices))
        for d in devices:
            cmd_line = "python pcap_pyqmflow.py -i %s -l %s " % (d, LICENCE_FILE)
            cmd_line = cmd_line + "--tenant-id '%s' --user-id '%s' --instance-id '%s'" % (tenant_id, user_id, instance_id)
            self.children[d] = subprocess.Popen(cmd_line, shell=True)

    def _disable_spotlight(self, tenant_id, user_id, instance_id, devices):
        LOG.info('_disable_spotlight %s %s %s', tenant_id, instance_id, str(devices))
        for d in devices:
            if d in self.children:
                process = self.children[d]
                process.send_signal(signal.SIGTERM)
                process.wait()
                del self.children[d]


def main():
    nsa = NetworkSpotlightAgent()
    MQHooks.append(nsa)
    run_listener("nova", "compute.#")


if __name__ == '__main__':
    main()
