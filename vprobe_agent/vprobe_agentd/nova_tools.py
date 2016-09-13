#!/usr/bin/env python
from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
from novaclient.v2.servers import ServerManager
import socket
import ConfigParser


def _get_client():
    config = ConfigParser.ConfigParser()
    config.read('/etc/nova/nova.conf')
    AUTH_URL = config.get('keystone_authtoken', 'auth_uri') + '/v3'
    USERNAME = config.get('keystone_authtoken', 'username')
    PASSWORD = config.get('keystone_authtoken', 'password')
    PROJECT_NAME = config.get('keystone_authtoken', 'project_name')
    PROJECT_DOMAIN_NAME = config.get('keystone_authtoken', 'project_domain_name')
    USER_DOMAIN_NAME = config.get('keystone_authtoken', 'user_domain_name')

    VERSION = '2.1'
    auth = v3.Password(auth_url=AUTH_URL,
                      username=USERNAME,
                      password=PASSWORD,
                      project_name=PROJECT_NAME,
                      user_domain_name=USER_DOMAIN_NAME,
                      project_domain_name=PROJECT_DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return client.Client(VERSION, session=sess)

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
