from network_spotlight_agentd.protocols import protocols
from aggregator import _Aggregator

class HttpAggregator(_Aggregator):
    __protocol__ = protocols.http

    def metadata_cb(self, metadata):
        return super(HttpAggregator, self).metadata_cb(metadata)

    def aggregate(self, header, packet, metadata):
        return


