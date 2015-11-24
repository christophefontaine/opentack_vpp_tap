import datetime
import ConfigParser

_publisher_modules = []


def _setup():
    import importlib
    global _publisher_modules
    config = ConfigParser.ConfigParser()
    config.read('/etc/network_spotlight_agentd/network_spotlight.conf')
    publishers = [value.strip() for value in config.get("DEFAULT", "publishers").split(',')]
    _publisher_modules = [(publisher, importlib.import_module("network_spotlight_agentd.publishers." + publisher + "_publisher")) for publisher in publishers ]
    for (name, module) in _publisher_modules:
        module_config = {}
        for (name, param) in config.items(name):
            module_config[name] = param
        module.setup(module_config)
    


def publish(tenant_id, user_id, instance_id, blob, sample_name="network.visibility"):
    for (name, module) in _publisher_modules:
        module.publish(tenant_id, user_id, instance_id, blob, sample_name)


_setup()
