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


# cfg.CONF.register_opts(RPC_OPTS,
#                        group="publisher_rpc")
# cfg.CONF.register_opts(NOTIFIER_OPTS,
#                        group="publisher_notifier")
# cfg.CONF.import_opt('host', 'ceilometer.service')

resource_id = 'a5aa0e946dd611e5b2f2001e67e5c052' #uuid.uuid1().hex

samples = [sample.Sample(
            name='test42',
            type=sample.TYPE_CUMULATIVE,
            unit='B/s',
            volume=1,
            user_id='b6832a954218439ca76d4d3a277f625f',
            project_id='ffc59a3e6a4a4ebfb4550b4901bbfa68',
            resource_id = resource_id,
            timestamp=datetime.datetime.utcnow().isoformat(),
            resource_metadata={'name': 'TestPublish'},
        )]

for config_file in cfg.find_config_files('ceilometer'):
    print config_file


messaging.setup()

cfg.CONF.unregister_opts([cfg.StrOpt('telemetry_secret')], group="publisher")
cfg.CONF.register_opts([cfg.StrOpt('telemetry_secret', default='fc0e4142d8224be0')], group="publisher")
publisher = msg_publisher.SampleNotifierPublisher(netutils.urlsplit('__default__'))
c = context.RequestContext('admin','admin', is_admin=True)
# import pdb; pdb.set_trace()
publisher.publish_samples(c, samples)


