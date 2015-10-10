import datetime
import uuid
from oslo_context import context
from oslo_utils import netutils
from ceilometer import messaging, sample, service

from oslo_config import cfg

from ceilometer.publisher import messaging as msg_publisher

import logging
_LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

RESOURCE_ID = 'qosmos.network.l7'

global publisher
global c
messaging.setup()
cfg.CONF.unregister_opts([cfg.StrOpt('telemetry_secret')], group="publisher")
cfg.CONF.register_opts([cfg.StrOpt('telemetry_secret', default='fc0e4142d8224be0')], group="publisher")
_publisher = msg_publisher.SampleNotifierPublisher(netutils.urlsplit('__default__'))
c = context.RequestContext('admin','admin', is_admin=True)


samples = [sample.Sample(
               name='',
               type=sample.TYPE_CUMULATIVE,
               unit='GAUGE',
               volume=1,
               user_id="plop",
               project_id="toto",
               resource_id = RESOURCE_ID ,
               timestamp=datetime.datetime.utcnow().isoformat(),
               resource_metadata={"blob": "toto27"},
               )]


def publish(tenant_id, user_id, blob, sample_name="l7"):
    samples = [sample.Sample(
              name=sample_name,
              type=sample.TYPE_CUMULATIVE,
              unit='GAUGE',
              volume=1,
              user_id=user_id,
              project_id=tenant_id,
              resource_id = RESOURCE_ID ,
              timestamp=datetime.datetime.utcnow().isoformat(),
              resource_metadata={"blob": blob},
              )]

    _publisher.publish_samples(c, samples)
