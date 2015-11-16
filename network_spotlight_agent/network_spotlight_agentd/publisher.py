import datetime
from Queue import Queue
from oslo_config import cfg
from oslo_context import context
from oslo_utils import netutils
from ceilometer import messaging, sample
from ceilometer.publisher import messaging as msg_publisher
from horizon.utils.memoized import memoized

from protocols import protocols as p

import logging
LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def _setup():
    import re
    telemetry_secret = None
    prog = re.compile('^metering_secret=(.*)$')
    for config_file in cfg.find_config_files('ceilometer'):
        LOG.info('config_file %s'%config_file)
        with open(config_file, "r") as cfgfile:
            for line in cfgfile.read().split('\n'):
                m = prog.match(line)
                if m is not None:
                    telemetry_secret = m.group(1)
                    LOG.info('telemetry_secret found')
                    break
    if telemetry_secret is not None:
        cfg.CONF.unregister_opts([cfg.StrOpt('telemetry_secret')],
                                  group="publisher")
        cfg.CONF.register_opts([cfg.StrOpt('telemetry_secret',
                                default=telemetry_secret)],
                               group="publisher")
        LOG.info("Set telemetry_secret to %s" % telemetry_secret)
    else:
        raise Exception('metering_secret NOT FOUND')
    messaging.setup()


@memoized
def _publisher():
    _setup()
    url = netutils.urlsplit('__default__')
    return msg_publisher.SampleNotifierPublisher(url)


@memoized
def _context():
    return context.RequestContext('admin', 'admin', is_admin=True)


def publish(tenant_id, user_id, instance_id, blob, sample_name="network.visibility"):
    metadatas = {}
    metadatas['app_name'] =  str(p.proto_from_id(int(blob['app_id'])))
    metadatas['flow_sig'] = blob['flow_sig']

    for (layer_id, attribute_id) in blob['metadata'].keys():
        layer =  p.proto_from_id(int(layer_id,))
        attribute = layer.attr_from_id(int(attribute_id))
        metadatas[str(layer)+"_"+str(attribute)] = blob['metadata'][(layer_id, attribute_id)]

    visibility_sample = sample.Sample(
               name=sample_name,
               type=sample.TYPE_GAUGE,
               unit='',
               volume=1,
               user_id=user_id,
               project_id=tenant_id,
               resource_id=instance_id,
               timestamp=datetime.datetime.utcnow().isoformat(),
               resource_metadata=metadatas,
               )
    LOG.info(metadatas)
    _publisher().publish_samples(_context(), [visibility_sample])
