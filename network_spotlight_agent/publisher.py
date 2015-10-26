import datetime
from oslo_config import cfg
from oslo_context import context
from oslo_utils import netutils
from ceilometer import messaging, sample
from ceilometer.publisher import messaging as msg_publisher
from horizon.utils.memoized import memoized
import logging
_LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def _setup():
    import re
    telemetry_secret = None
    prog = re.compile('^[metering|telemetry]_secret=(.*)$')
    for config_file in cfg.find_config_files('ceilometer'):
        with open(config_file, "r") as cfgfile:
            for line in cfgfile.read().split('\n'):
                m = prog.match(line)
                if m is not None:
                    telemetry_secret = m.group(1)
                    _LOG.debug('telemetry_secret found')
                    break
    _LOG.debug("telemetry_secret is %s" % str(telemetry_secret))
    cfg.CONF.unregister_opts([cfg.StrOpt('telemetry_secret')],
                              group="publisher")
    if telemetry_secret is not None:
        cfg.CONF.register_opts([cfg.StrOpt('telemetry_secret',
                                default=telemetry_secret)],
                               group="publisher")
        _LOG.info("Set telemetry_secret to %s" % telemetry_secret)
    else:
        # fc0e4142d8224be0
        cfg.CONF.register_opts([cfg.StrOpt('telemetry_secret',
                                default="fc0e4142d8224be0")],
                               group="publisher")
        _LOG.info("Set telemetry_secret to %s" % "fc0e4142d8224be0")
    
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
    _publisher().publish_samples(_context(), samples)
