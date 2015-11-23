import datetime
import ConfigParser

_publisher_modules = []


def _setup():
    import importlib
    global _publisher_modules
    config = ConfigParser.ConfigParser()
    config.read('/etc/network_spotlight_agentd/network_spotlight.conf')
    publishers = [value.strip() for value in config.get("DEFAULT", "publishers").split(',')]
    _publisher_modules = [importlib.import_module("network_spotlight_agentd.publishers." + publisher + "_publisher") for publisher in publishers ]
    for puslisher_module in _publisher_modules:
        puslisher_module.setup(config.items(publisher))
    


def publish(tenant_id, user_id, instance_id, blob, sample_name="network.visibility"):
    for puslisher_module in _publisher_modules:
        puslisher_module.publish(tenant_id, user_id, instance_id, blob, sample_name)


_setup()
