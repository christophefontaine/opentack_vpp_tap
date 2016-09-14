OpenStack Dashboard plugin for vprobe project
=============================================

How to use with Horizon on server:
----------------------------------

Use pip to install the package on the server running Horizon. Then either copy
or link the files in vprobe_dashboard/enabled to
vprobe_dashboard/local/enabled. This step will cause the Horizon service to
pick up the vprobe plugin when it starts.

How to use with devstack:
-------------------------
Here is an example of a local.conf: 
.. code-block::
  [[local|localrc]]
  ADMIN_PASSWORD=rdcolab
  DATABASE_PASSWORD=$ADMIN_PASSWORD
  RABBIT_PASSWORD=$ADMIN_PASSWORD
  SERVICE_PASSWORD=$ADMIN_PASSWORD
  # FIXED_RANGE="10.22.78.0/24"
  # NETWORK_GATEWAY=10.22.0.1
  disable_service n-net q-agt
  disable_service cinder c-sch c-api c-vol swift
  disable_service tempest
  disable_service n-net
  NEUTRON_CREATE_INITIAL_NETWORKS=False
  LIBVIRT_TYPE=kvm
  enable_plugin networking-vpp https://github.com/iawells/networking-vpp.git
  ENABLED_SERVICES+=,q-svc,q-meta,q-dhcp
  Q_PLUGIN=ml2
  Q_ML2_TENANT_NETWORK_TYPE=vlan
  ML2_VLAN_RANGES=physnet:100:200
  Q_ML2_PLUGIN_EXT_DRIVERS=
  Q_ML2_PLUGIN_MECHANISM_DRIVERS=vpp
  Q_ML2_PLUGIN_TYPE_DRIVERS=vlan,flat
  VLAN_TRUNK_IF='GigabitEthernet8/0/0'
  MECH_VPP_PHYSNETLIST=physnet:GigabitEthernet8/0/0
  MECH_VPP_AGENTLIST=localhost
  MECH_VPP_DEBUG=True
  QEMU_USER=root
  QEMU_GROUP=root
  ENABLED_SERVICES+=,heat,h-api,h-api-cfn,h-api-cw,h-eng
  enable_plugin tap https://github.com/christophefontaine/opentack_vpp_tap
  # OFFLINE=True
  # RECLONE=False
