from network_spotlight_agentd.protocols import protocols
from aggregator import _Aggregator
from copy import deepcopy
import logging
LOG = logging.getLogger(__name__)


HTTP_REQUEST = (int(protocols.http), int(protocols.http.request))

class HttpAggregator(_Aggregator):
    __protocol__ = protocols.http

    def aggregate(self, flow, md_dict):
        ret_flow = None
        if HTTP_REQUEST in md_dict['metadata']:
            if md_dict['pkt_way'] == 'client':
                if md_dict['metadata'][HTTP_REQUEST] == 'start':
                    if 'client_request_end' in flow:
                        del flow['client_request_end']
                    if 'client_request_start' in flow:
                        ret_flow = deepcopy(flow)
                        self._clean(flow)
                    else:
                        flow['client_request_start'] = True
            if md_dict['metadata'][HTTP_REQUEST] == 'end':
                ret_flow = deepcopy(flow)
                self._clean(flow)
                if 'client_request_start' in flow:
                    del flow['client_request_start']
                flow['client_request_end'] = True
            del md_dict['metadata'][HTTP_REQUEST]
        elif 'expired' in md_dict:
            ret_flow = flow
        del md_dict['pkt_way']
        _Aggregator.update(flow, md_dict)
        return ret_flow
