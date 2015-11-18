from network_spotlight_agentd.protocols import protocols
import collections

class _Aggregator(object):
    __protocol__ = 0

    @staticmethod
    def update(d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = _Aggregator.update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    @property
    def protocol(self):
        return self.__protocol__

    def aggregate(self, flow, md_dict):
        _Aggregator.update(flow, md_dict)
        if 'expired' in flow:
            return flow
        else:
            return None

    def _clean(self, flow):
        for (proto, attribute) in flow['metadata'].keys():
            if proto == int(self.__protocol__):
                del flow['metadata'][(proto, attribute)]
        try:
            flow["client-bytes"] = 0
            flow["server-bytes"] = 0
            flow['flow_start_time'] = flow['flow_end_time']
        except:
            pass


class AggregatorBase(_Aggregator):
    __protocol__ = protocols.base
    def aggregate(self, flow, md_dict):
        return super(AggregatorBase, self).aggregate(flow, md_dict)
