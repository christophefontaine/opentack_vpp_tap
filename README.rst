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

Add the following to your devstack ``local.conf`` file::

    enable_plugin vprobe-dashboard http://gitlab.foret/fontaine/network_visibility.git
