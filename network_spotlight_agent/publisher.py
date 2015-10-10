import datetime
import json
from oslo_config import cfg
from oslo_context import context
from oslo_utils import netutils
from ceilometer import messaging, sample
from ceilometer.publisher import messaging as msg_publisher

import logging
_LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


cfg.CONF.unregister_opts([cfg.StrOpt('telemetry_secret')], group="publisher")
cfg.CONF.register_opts([cfg.StrOpt('telemetry_secret',
                        default='fc0e4142d8224be0')],
                        group="publisher")
messaging.setup()
_publisher = msg_publisher.SampleNotifierPublisher(
                 netutils.urlsplit('__default__'))

c = context.RequestContext('admin', 'admin', is_admin=True)


def publish(tenant_id, user_id, instance_id, blob, sample_name="l7"):
    samples = [sample.Sample(
               name=sample_name,
               type=sample.TYPE_CUMULATIVE,
               unit='GAUGE',
               volume=1,
               user_id=user_id,
               project_id=tenant_id,
               resource_id=instance_id,
               timestamp=datetime.datetime.utcnow().isoformat(),
               resource_metadata={"flow_sig": blob['flow_sig'],
                                  "ixe_md": blob['metadata']},
               )]
    _publisher.publish_samples(c, samples)
