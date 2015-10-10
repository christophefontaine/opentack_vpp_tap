#!/usr/bin/env python
# Copyright  Qosmos 2000-2015 - All rights reserved

import platform
import logging
import json
import subprocess
import signal
import pcap_pyqmflow
from rabbit_listener import run_listener, MQHooks
LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

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

    def _vm_is_local(self, hostname):
        LOG.info('_vm_is_local: ' + hostname)
        return hostname == platform.node()

    def _enable_spotlight(self, tenant_id, user_id, instance_id, devices):
        LOG.info('_enable_spotlight %s %s %s', tenant_id, instance_id, str(devices))
        for d in devices:
            outfile = open(instance_id + "_" + d + ".log", 'w')
            dpi = pcap_pyqmflow.DPIThread(d)
            dpi.tenant_id = tenant_id
            dpi.user_id = user_id
            cmd_line = "python pcap_pyqmflow.py -i %s -l %s " % (d, LICENCE_FILE)
            cmd_line = cmd_line + "--tenant-id %s --user-id %s " % (tenant_id, user_id)
            self.children[d] = subprocess.Popen(cmd_line, stdout=outfile, shell=True)

    def _disable_spotlight(self, tenant_id, user_id, instance_id, devices):
        LOG.info('_disable_spotlight %s %s %s', tenant_id, instance_id, str(devices))
        for d in devices:
            if d in self.children:
                process = self.children[d]
                process.send_signal(signal.SIGTERM)
                process.wait()
                del self.children[d]


def main():
    pcap_pyqmflow.setup(LICENCE_FILE)
    nsa = NetworkSpotlightAgent()
    MQHooks.append(nsa)
    run_listener("nova", "compute.#")
   

if __name__ == '__main__':
    main()
