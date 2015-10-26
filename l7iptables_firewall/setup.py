#!/usr/bin/env python
import os
from setuptools import setup, find_packages

setup(
    name = "l7_iptables_firewall",
    version = "0.1.a0.dev-0",
    author = "Christophe Fontaine",
    author_email = "christophe.fontaine@qosmos.com",
    description = ("Extensions for neutron.agent.firewall.NoopFirewallDriver,"
                   "neutron.agent.linux.iptables_firewall.IptablesFirewallDriver, "
                   "neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver"),
    license = "Proprietary",
    keywords = "",
    url = "",
    long_description="",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities"
    ],
    provides = ['l7_iptables_firewall'],
    zip_safe=False,
#    packages=['l7_iptables_firewall'],
    packages=find_packages(),
)
