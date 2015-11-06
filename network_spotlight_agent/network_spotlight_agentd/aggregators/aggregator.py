from network_spotlight_agentd.protocols import protocols

class _Aggregator(object):
    __protocol__ = 0

    @property
    def protocol(self):
        return self.__protocol__

    def metadata_cb(self, metadata):
        __doc__ = "Return if publish should be done"
        return "expired" in metadata

    def aggregate(self, header, packet, metadata):
        raise Exception("Abstract aggregate method called")


class AggregatorBase(_Aggregator):
    __protocol__ = protocols.base
    def metadata_cb(self, metadata):
        return super(AggregatorBase, self).metadata_cb(metadata)

    def aggregate(self, header, packet, metadata):
        return
