import ConfigParser
from ..protocols import protocols as p
import uuid
import json
from datetime import datetime
from elasticsearch import Elasticsearch

import logging
LOG = logging.getLogger(__name__)

_config = {}
_es = None


def setup(user_config):
    global _config
    global _es
    _config = user_config
    for param in ['server', 'port', 'index']:
        if not param  in _config:
            raise Exception("Missing _configuration parameter: '%s'" % param)
    LOG.info("elasticsearch publisher - " + str(_config['server']) + ':' +  str(_config['port']) )
    _es = Elasticsearch()


def publish(tenant_id, user_id, instance_id, blob, sample_name="network.visibility"):
    # prepare payload
    payload = { '_id': str( uuid.uuid1()),
                '_index': _config['index'],
                '_type': 'flow',
                'timestamp': datetime.now(),
                'tenant_id': tenant_id,
                'user_id': user_id,
                'instance_id': instance_id }

    # if 'ttl' in _config:
    #    payload['_ttl'] = _config['ttl']

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
    
    LOG.debug(str(payload))
    r =_es.index(index=payload['_index'], doc_type='flow', id=payload['_id'], body=payload)
    LOG.debug(str(r))

