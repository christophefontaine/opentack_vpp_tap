#!/usr/bin/env python
# Copyrights Qosmos 2015
import ixe.pyixe as qm

import optparse
import sys
import signal
import traceback
import re
import pcapy
import impacket
from impacket.ImpactDecoder import EthDecoder
import publisher
import imp
from protocols import protocols as ixe_protocols

__author__ = "Christophe Fontaine"
__email__ = "christophe.fontaine@qosmos.com"
__company__ = "Qosmos"
import logging
LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

_ixe = None

import collections
def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


colours={"default":"",
         "blue":   "\x1b[01;34m",
         "cyan":   "\x1b[01;36m",
         "green":  "\x1b[01;32m",
         "red":    "\x1b[01;05;37;41m"}

def dump_dict(flow):
    colors = ["\x1b[01;34m", "\x1b[01;33m", "\x1b[01;35m", "\x1b[01;36m", "\x1b[01;32m", "\x1b[01;37m", "\x1b[01;05;37;41m"]
    ret_str = '{'
    for el in flow.keys():
        if not el.startswith('_'):
            if el == 'flow_sig':
               ret_str = ret_str + str(el) + ": " + colors[hash(str(flow[el])) % len(colors)] + str(flow[el]) +  "\x1b[00m "
            else:
                ret_str = ret_str + str(el) + ": " + str(flow[el]) + " "
    ret_str = ret_str + '}'
    return ret_str


class IXE():
    def __init__(self, interface):
        self.cap = pcapy.open_live(interface, 65536, 1, 0)
        self.cap.setfilter('ip')
        self._flows = {}
        self._aggregators = {}
        # Example to retreive metadatas from flows
        qm.set_callback(self.metadata_cb)
        try:
            self._add_application_specific_ixe_protocols()
            self._build_aggregators()
            SUBSCRIBED_METADATAS = imp.load_source("extracted_metadata", "/etc/network_spotlight_agentd/extracted_metadata.py").SUBSCRIBED_METADATAS
        except Exception:
            LOG.error('*********************************** ERROR ****************************************')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            LOG.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            raise
        for attribute in SUBSCRIBED_METADATAS:
            LOG.info("Subscribing to %s.%s (%d.%d)" % (str(attribute._parent), str(attribute), int(attribute._parent), int(attribute)))
            qm.md_subscribe(int(attribute._parent), int(attribute))

    def _add_application_specific_ixe_protocols(self):
        from protocols import Protocols
        metadata_index = 65536
        application_specific_attributes = [(ixe_protocols.base, 'client_bytes'), (ixe_protocols.base, 'server_bytes'),
                                           (ixe_protocols.ip, 'client_port'), (ixe_protocols.ip, 'server_port')]
        for (proto, attr) in application_specific_attributes:
             proto.__dict__[attr] = Protocols.Protocol(attr, metadata_index, proto)
             metadata_index += 1

    def _build_aggregators(self):
        import inspect
        import aggregators
        self._aggregators = {}
        for subpackage in aggregators.__dict__.values():
            if inspect.ismodule(subpackage):
                for (aggregator_name, aggregator) in inspect.getmembers(subpackage, inspect.isclass):
                    print  aggregator_name + "-"+ str(aggregator)
                    try:
                        instance = aggregator()
                        self._aggregators[int(instance.protocol)] = instance
                        print self._aggregators
                    except:
                        pass

    def metadata_cb(self, md_dict):
        """
        Metadata Extraction:
            You must set this function as callback first and
            subscribe to a metadata before receiving any metadata
            This may be done with methods 'qm.set_callback'
            and 'qm.md_subscribe'
        """
        try:
            if len(md_dict['metadata']) > 0:
                 LOG.debug('***************************************************************************************************\nmetadata_cb -- ' + dump_dict(md_dict))
            flow_sig = md_dict['flow_sig']
            if not (flow_sig in self._flows.keys()):
               self._flows[flow_sig] = { "app_id":0, "metadata": {}}
            flow = self._flows[flow_sig]
            aggregator = self._aggregators.get(md_dict["app_id"] , self._aggregators[int(ixe_protocols.base)])
            aggegrated_data = aggregator.aggregate(flow, md_dict)

            if aggegrated_data:
                publisher.publish(self.tenant_id or 'admin',
                                  self.user_id or 'admin',
                                  self.instance_id,
                                  aggegrated_data)
            if "expired" in md_dict :
                del self._flows[flow_sig]

        except Exception:
            LOG.error('*********************************** ERROR ****************************************')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            LOG.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    def _new_flow(self, sig, header, packet):
        eth = EthDecoder().decode(packet)
        ip=eth.child()
        metadata = {}
        metadata[(int(ixe_protocols.ip), int(ixe_protocols.ip.client_addr))] = ip.get_ip_src()
        metadata[(int(ixe_protocols.ip), int(ixe_protocols.ip.server_addr))] = ip.get_ip_dst()
        transport = ip.child()
        if ip.get_ip_p() == impacket.ImpactPacket.UDP.protocol:
             metadata[(int(ixe_protocols.ip), int(ixe_protocols.ip.client_port))] = transport.get_uh_sport()
             metadata[(int(ixe_protocols.ip), int(ixe_protocols.ip.server_port))] = transport.get_uh_dport()
        if ip.get_ip_p() == impacket.ImpactPacket.TCP.protocol:
             metadata[(int(ixe_protocols.ip), int(ixe_protocols.ip.client_port))] = transport.get_th_sport()
             metadata[(int(ixe_protocols.ip), int(ixe_protocols.ip.server_port))] = transport.get_th_dport()
        metadata[(int(ixe_protocols.base), int(ixe_protocols.base.client_bytes))] = 0
        metadata[(int(ixe_protocols.base), int(ixe_protocols.base.server_bytes))] = 0

        self._flows[sig] = { "app_id":0, "metadata": metadata,
                             "flow_start_time": float(header.getts()[0] + (header.getts()[1]/1000000.)) }        

    def run(self):
        while True:
            try:
                header, packet = self.cap.next()
                # Analyse packet
                ret = qm.process_packet(pdata=packet, time=header.getts())
                if ret:
                    (sig, offloaded, result, proto, way) = ret
                    if not (sig in self._flows):
                        self._new_flow(sig, header, packet)
                    self._flows[sig]["flow_end_time"] = float(header.getts()[0] + (header.getts()[1]/1000000.))
                    if way == "client":
                        byte_count = (int(ixe_protocols.base), int(ixe_protocols.base.client_bytes))
                    else:
                        byte_count = (int(ixe_protocols.base), int(ixe_protocols.base.server_bytes))
                    self._flows[sig]['metadata'][byte_count] += len(packet)
                    delta_ts = self._flows[sig]["flow_end_time"] - self._flows[sig]["flow_start_time"]
                    self._flows[sig]['metadata'][(int(ixe_protocols.base), int(ixe_protocols.base.duration))] = delta_ts
            except pcapy.PcapError:
                LOG.error("pcapy.PcapError")
                pass
            except Exception:
                LOG.error('*********************************** ERROR ****************************************')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                LOG.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    def stop(self):
        for sig in self._flows:
            flow = self._flows[sig]
            publisher.publish(self.tenant_id or 'admin',
                              self.user_id or 'admin',
                              self.instance_id,
                              flow)


def setup(license_file):
    try:
        if license_file is not None:
            LOG.info(license_file)
            serial_number = re.match("^.*/?(Q[a-zA-Z\-\d]*)-\d*.bin$",
                                     license_file).group(1)
            LOG.info(serial_number)
            qm.set_license(filename=license_file, serial=serial_number)
        qm.init()
    except Exception as e:
        LOG.error(str(e))
        return


def cleanup():
    qm.exit()
    return


def sigterm_handler(_signo, _stack_frame):
    LOG.info("Worker - sigterm_handler - Quit")
    if _ixe:
        _ixe.stop()
    cleanup()
    LOG.info("Worker - sigterm_handler - Bye")
    # Raises SystemExit(0):
    sys.exit(0)


def main():
    global _ixe
#    signal.signal(signal.SIGTERM, sigterm_handler)
    parser = optparse.OptionParser()
    parser.add_option('-i', '--interface',
                      dest='interface',
                      help='Set interface on which we will listen')
    parser.add_option('-l', '--license',
                      dest='license',
                      help='Set licence file')
    parser.add_option('--tenant-id')
    parser.add_option('--user-id')
    parser.add_option('--instance-id')
    (options, args) = parser.parse_args()
    setup(options.license)
    try:
        _ixe = IXE(options.interface)
        _ixe.tenant_id = options.tenant_id
        _ixe.user_id = options.user_id
        _ixe.instance_id = options.instance_id
        _ixe.run()
    except KeyboardInterrupt:
        LOG.info('KeyboardInterrupt')
    finally:
        _ixe.stop()
        cleanup()
    LOG.info("Worker - Bye")


if __name__ == '__main__':
    main()
