from oslo_log import log as logging
from neutron.agent.firewall import NoopFirewallDriver
from neutron.agent.linux.iptables_firewall import IptablesFirewallDriver, OVSHybridIptablesFirewallDriver
LOG = logging.getLogger(__name__)


class L7_NoopFirewallDriver(NoopFirewallDriver):
    """ Extension of NoopFirewallDriver to add visibility rules"""


class L7_IptablesFirewallDriver(IptablesFirewallDriver):
    """ Extension of IptablesFirewallDriver to add visibility
        and enforcement rules"""
    def _add_chain(self, port, direction):
        IptablesFirewallDriver._add_chain(self, port, direction)
        dpi_rule_ipv4 = ['-m l7 --l7proto 1 -j DROP']
        dpi_rule_ipv6 = ['']
        self._add_rules_to_chain_v4v6(self._port_chain_name(port, direction),
                                      dpi_rule_ipv4, dpi_rule_ipv6,
                                      comment="DPI Visibility and Microsegmentation")


class L7_OVSHybridIptablesFirewallDriver(L7_IptablesFirewallDriver, OVSHybridIptablesFirewallDriver):
    """ Extension of OVSHybridIptablesFirewallDriver to add visibility
        and enforcement rules
        Nothing to add
    """
