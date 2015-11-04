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
    name = "networkspotlight",
    version = "0.1.a0.dev-3",
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
    provides = ['networkspotlight'],
    zip_safe=False,
    packages=['networkspotlight'],
    package_data={'networkspotlight': ['templates/networkspotlight/*', 'static/networkspotlight/*']},
    data_files=[('/usr/share/openstack-dashboard/openstack_dashboard/local/enabled', ['_99_nsa.py'])],
)
