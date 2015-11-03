#!/usr/bin/env python
# Copyrights Qosmos 2015
import ixe.pyqmflow as qm

import optparse
import sys
import traceback
import re
import pcapy
import publisher
from conf_metadata import SUBSCRIBED_METADATAS
from protocols import protocols as p

__author__ = "Christophe Fontaine"
__email__ = "christophe.fontaine@qosmos.com"
__company__ = "Qosmos"


import logging
LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


import collections
def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


class IXE():
    def __init__(self, interface):
        self.cap = pcapy.open_live(interface, 65536, 1, 0)
        self._flows = {}
        # Example to retreive metadatas from flows
        qm.set_callback(self.metadata_cb)
        for protocol in SUBSCRIBED_METADATAS:
            LOG.info("Subscribing to %s-%s" % (str(protocol._parent), str(protocol)))
            qm.md_subscribe(int(protocol._parent), int(protocol))

    def metadata_cb(self, md_dict):
        """
        Metadata Extraction:
            You must set this function as callback first and
            subscribe to a metadata before receiving any metadata
            This may be done with methods 'qm.set_callback'
            and 'qm.md_subscribe'
        """
        try:
            LOG.info("metadata_cb " + str(md_dict))
            if "expired" in md_dict:
                publisher.publish(self.tenant_id or 'admin',
                                  self.user_id or 'admin',
                                  self.instance_id,
                                  self._flows[md_dict['flow_sig']])
                del self._flows[md_dict['flow_sig']]
            else:
                if not md_dict['flow_sig'] in self._flows:
                    self._flows[md_dict['flow_sig']] = {}
                update(self._flows[md_dict['flow_sig']], md_dict)
                
        except Exception:
            LOG.error('*********************************** ERROR ****************************************')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            LOG.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    def run(self):
        while True:
            try:
                header, packet = self.cap.next()
                # Analyse packet
                qm.process_packet(pdata=packet, time=header.getts())
            except pcapy.PcapError:
                pass
            except Exception:
                LOG.error('*********************************** ERROR ****************************************')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                LOG.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))


def setup(license_file):
    try:
        if license_file is not None:
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


def main():
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
        ixe = IXE(options.interface)
        ixe.tenant_id = options.tenant_id
        ixe.user_id = options.user_id
        ixe.instance_id = options.instance_id
        ixe.run()
    except KeyboardInterrupt:
        LOG.debug('KeyboardInterrupt')
    finally:
        cleanup()


if __name__ == '__main__':
    main()