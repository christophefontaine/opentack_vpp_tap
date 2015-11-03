from os import environ
from ceilometerclient import client
from pprint import pprint
VERSION = '2'
OS_USERNAME = ''
OS_PASSWORD = ''
OS_TENANT_NAME = ''
OS_AUTH_URL = ''


def main():
    cclient = client.get_client(VERSION,
                                os_username=OS_USERNAME,
                                os_password=OS_PASSWORD,
                                os_tenant_name=OS_TENANT_NAME,
                                os_auth_url=OS_AUTH_URL)
    # import pdb; pdb.set_trace()
    pprint(cclient.samples.list())


if __name__ == "__main__":
    for os_var in ['OS_USERNAME',
                   'OS_PASSWORD',
                   'OS_TENANT_NAME',
                   'OS_AUTH_URL']:
        if os_var not in environ.keys():
            raise Exception('Please source keystonerc_admin '
                            'before launching this app')
        globals()[os_var] = environ[os_var]
    main()
