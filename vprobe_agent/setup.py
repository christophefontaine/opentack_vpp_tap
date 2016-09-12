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
    name = "vprobe_agentd",
    version = "0.1.a0.dev-4",
    author = "Christophe Fontaine",
    author_email = "christophe.fontaine@qosmos.com",
    description = (""),
    license = "Proprietary",
    keywords = "",
    url = "",
    long_description="Agent which configures vpp to enable port mirroring",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities"
    ],
    provides = ['vprobe_agentd'],
    zip_safe = False,
    packages = find_packages(exclude=["ut_*"]),
    install_requires=["requests", "pika"],
    data_files = [('/etc/vprobe_agentd/', ['etc/vprobe.conf']), ],
    entry_points = {
        'console_scripts': [
            'vprobe_agentd = vprobe_agentd.vprobe_agent:main',
        ]
    }
)
