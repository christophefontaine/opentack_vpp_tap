from datetime import datetime
import socket
import uuid
from horizon.utils.memoized import memoized

from ..protocols import protocols as p

import logging
LOG = logging.getLogger(__name__)


class Context():
    def __init__(self):
        self.server = None
        self.port = None
        self.facility = None
        self.level = None
        

_context = Context()

class Facility:
  KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, \
  LPR, NEWS, UUCP, CRON, AUTHPRIV, FTP = range(12)
  LOCAL0, LOCAL1, LOCAL2, LOCAL3, \
  LOCAL4, LOCAL5, LOCAL6, LOCAL7 = range(16, 24)


class Level:
  "Syslog levels"
  EMERG, ALERT, CRIT, ERR, \
  WARNING, NOTICE, INFO, DEBUG = range(8)


def setup(user_config):    
    for parameter in ['server', 'port', 'facility', 'level']:
        if not parameter in user_config:
            raise Exception("Missing parameter '%s'" % parameter)
    _context.server = user_config['server']
    _context.port = int(user_config['port'])
    if not user_config['facility'].upper() in [i for i in dir(Facility) if not i.startswith('_')]:
        raise Exception("Wrong paramter for 'facility'")
    else:
        _context.facility = Facility.__dict__[user_config['facility'].upper()]
    if not user_config['level'].upper() in [i for i in dir(Level) if not i.startswith('_')]:
        raise Exception("Wrong paramter for 'level'")
    else:
        _context.level = Level.__dict__[user_config['level'].upper()]
    _context.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def publish(tenant_id, user_id, instance_id, blob, sample_name="network.visibility"):
    # prepare payload
    payload = { '_id': str( uuid.uuid1()),
                '_type': 'flow',
                'timestamp': datetime.now(),
                'tenant_id': tenant_id,
                'user_id': user_id,
                'instance_id': instance_id }

    payload['flow_sig'] = blob['flow_sig']
    payload['app_name'] =  str(p.proto_from_id(int(blob['app_id'])))
    payload['proto_path'] = None
    for proto in blob['proto_path']:
        if payload['proto_path'] is None:
            payload['proto_path'] = str(p.proto_from_id(proto))
        else:
            payload['proto_path'] = payload['proto_path'] + '.' + str(p.proto_from_id(proto))

    for (layer_id, attribute_id) in blob['metadata'].keys():
        layer =  p.proto_from_id(int(layer_id,))
        attribute = layer.attr_from_id(int(attribute_id))
        if not str(layer) in payload:
            payload[str(layer)] = {}
        payload[str(layer)][str(attribute)] = blob['metadata'][(layer_id, attribute_id)]

    data = "<%d>%s" % (_context.level + _context.facility*8, str(payload))
    _context.socket.sendto(data, (_context.server, _context.port))
