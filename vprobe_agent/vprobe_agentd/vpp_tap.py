import sys
import etcd
import ConfigParser
import socket
import json
import vpp_papi
from portmirroring import *
portmirroring = sys.modules['portmirroring']


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class VPPTapClassifier(object):
    def __init__(self, config_file = '/etc/vprobe/vprobe.conf'):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        try:
            self.dest_sw_if_name = config.get("DEFAULT", "vpp_target_interface")
        except:
            self.dest_sw_if_name = 'vpp-pm'    
        self.tap_init()

    def tap_init(self):
        r = vpp_papi.connect('VPPTapInit')
        r = vpp_papi.tap_connect(1, self.dest_sw_if_name, '', 0, 0)
        if r.retval != 0:
            raise Exception('Tap interface named %s already exists' % self.dest_sw_if_name)
        tap_if_index = r.sw_if_index
        vpp_papi.sw_interface_set_flags(tap_if_index, 1, 1, 0)
        portmirroring.pm_conf(tap_if_index, 0)

        mask = 0
        pm_in_hit_idx = vpp_papi.get_next_index('l2-input-classify', 'pm-in-hit').next_index
        pm_out_hit_idx = vpp_papi.get_next_index('l2-output-classify', 'pm-out-hit').next_index

        self.cl0 = vpp_papi.classify_add_del_table(1, 0xffffffff, 64, 1024*1024, 0, 1, 0xffffffff, pm_in_hit_idx, mask)
        self.cl1 = vpp_papi.classify_add_del_table(1, 0xffffffff, 64, 1024*1024, 0, 1, 0xffffffff, pm_out_hit_idx, mask)
        vpp_papi.disconnect()

    def etcd_sw_index_from_name(self, sw_if_name):
        c = etcd.Client()
        path = '/networking-vpp/state/'+socket.gethostname()+'/ports/'
        ports = c.read(path)
        c = None
        for port in ports.children:
            if port.key.startswith(path + sw_if_name[3:]):
                port_idx = json.loads(port.value)['iface_idx']
                break
        else:
            print('Port %s not found' % sw_if_name)
            port_idx = -1

        return port_idx
        
    def tap_interface(self, sw_if_name):
        r = vpp_papi.connect('VPPTapInterface')
        is_input = True
        is_output = False
        # sw_if_index = vpp_papi.sw_interface_dump(1, sw_if_name)[0].sw_if_index
        sw_if_index = self.etcd_sw_index_from_name(sw_if_name)
        if sw_if_index != -1:
            vpp_papi.classify_set_interface_l2_tables(sw_if_index, int(self.cl0.new_table_index), 0xffffffff, 0xffffffff, is_input)
            vpp_papi.classify_set_interface_l2_tables(sw_if_index, int(self.cl1.new_table_index), 0xffffffff, 0xffffffff, is_output)
        vpp_papi.disconnect()

    def untap_interface(self, sw_if_name):
        r = vpp_papi.connect('VPPUnTapInterface')
        is_input = 1
        is_output = 0
        # sw_if_index = vpp_papi.sw_interface_dump(1, sw_if_name)[0].sw_if_index
        sw_if_index = self.etcd_sw_index_from_name(sw_if_name)
        if sw_if_index != -1:
            vpp_papi.classify_set_interface_l2_tables(sw_if_index, 0xffffffff, 0xffffffff, 0xffffffff, is_input)
            vpp_papi.classify_set_interface_l2_tables(sw_if_index, 0xffffffff, 0xffffffff, 0xffffffff, is_output)
        vpp_papi.disconnect()
