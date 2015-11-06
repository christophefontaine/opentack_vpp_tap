#!/usr/bin/env python
import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "network_spotlight_agentd",
    version = "0.1.a0.dev-2",
    author = "Christophe Fontaine",
    author_email = "christophe.fontaine@qosmos.com",
    description = (""),
    license = "Proprietary",
    keywords = "",
    url = "",
    long_description=read('README'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities"
    ],
    provides = ['network_spotlight_agentd'],
    zip_safe = False,
    packages = find_packages(exclude=["ut_*"]),
    install_requires=["requests", "pika", "pcapy", "impacket"],
    package_data = {'network_spotlight_agentd': ['ixe/pyqmflow.so', 'ixe/protodef.proto']},
    data_files = [('/etc/network_spotlight_agentd/', ['etc/extracted_metadata.py', 'etc/conf_rabbit.py']), ],
    entry_points = {
        'console_scripts': [
            'network_spotlight_agentd = network_spotlight_agentd.network_spotlight_agent:main',
            'network_spotlight_worker = network_spotlight_agentd.pcap_pyqmflow:main'
        ]
    }
)
