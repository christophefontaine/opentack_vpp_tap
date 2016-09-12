#!/usr/bin/env python
from novaclient import client
from novaclient.v2.servers import ServerManager
import socket
import ConfigParser

def _get_client():
    config = ConfigParser.ConfigParser()
    config.read('/etc/nova/nova.conf')
    AUTH_URL = config.get('keystone_authtoken', 'auth_uri')
    USERNAME = config.get('keystone_authtoken', 'admin_user')
    PASSWORD = config.get('keystone_authtoken', 'admin_password')
    PROJECT_ID = config.get('keystone_authtoken', 'admin_tenant_name')
    VERSION = '2'
    return client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)


def _get_vms(nova):
    return nova.servers.list(search_opts={'all_tenants': 1, 'host': socket.gethostname()})


def enable_vprobes():
    nova = _get_client()
    for vm in _get_vms(nova):
        vm_info = vm.to_dict()
        try:
            if str(vm_info['metadata']['tap-enable']) == 'True':
                nova.servers.set_meta_item(vm, 'tap-enable', 'True')
        except:
            pass 
