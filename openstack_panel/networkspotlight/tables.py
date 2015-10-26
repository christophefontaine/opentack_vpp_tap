from django.utils.translation import ugettext_lazy as _

from horizon import tables
from openstack_dashboard.api.nova import novaclient
import logging
LOG = logging.getLogger(__name__)


class NetworkVisibilityEnableAction(tables.Action):
    name = 'networkvisibility_enable_action'
    verbose_name = 'Enable Monitoring'

    def single(self, table, request, object_id):
        instance = table.get_object_by_id(object_id)
        instance.visibility_enabled = 'True'
	novaclient(request).servers.set_meta_item(str(instance.id), 'nsa', 'True')


class NetworkVisibilityDisableAction(tables.Action):
    name = 'networkvisibility_disable_action'
    verbose_name = 'Disable Monitoring'

    def single(self, table, request, object_id):
        instance = table.get_object_by_id(object_id)
        instance.visibility_enabled = 'False'
	novaclient(request).servers.set_meta_item(str(instance.id), 'nsa', 'False')


class ToggleNetworkVisibility(tables.BatchAction):
    name = "toggle_networkvisibility"
    icon = "pause"

    ENABLE = 0
    DISABLE = 1

    @staticmethod
    def action_present(count):
        LOG.warning("action_present")
        return (u"Enable Agent", u"Disable Agent",)

    @staticmethod
    def action_past(count):
        LOG.warning("action_past")
        return (u"Agent enabled", u"Agent disabled",)

    def allowed(self, request, instance=None):
        LOG.warning("allowed")
        if not instance:
            return False

        self.visibility_enabled = (instance.to_dict()['metadata']['nsa'] == 'True') or False
        instance.visibility_enabled = self.visibility_enabled
        if self.visibility_enabled:
            self.current_present_action = ToggleNetworkVisibility.DISABLE
        else:
            self.current_present_action = ToggleNetworkVisibility.ENABLE
        return True

    def action(self, request, instance_id):
        LOG.warning("action")
        if self.visibility_enabled:
            self.visibility_enabled = False
            novaclient(request).servers.set_meta_item(instance_id, 'nsa', 'False')
            self.current_past_action = ToggleNetworkVisibility.DISABLE
        else:
            self.visibility_enabled = True
            novaclient(request).servers.set_meta_item(instance_id, 'nsa', 'True')
            self.current_past_action = ToggleNetworkVisibility.ENABLE


class NetworkVisibilityLink(tables.LinkAction):
    name = 'networkvisibility_go_to_kibana'
    verbose_name = 'Go To Kibana'
    
    def get_link_url(self, datum=None):
        LOG.info(self)
        return 'http://kibana/'


class InstancesTable(tables.DataTable):
    tenant = tables.Column("tenant_name", verbose_name=_("Tenant"))
    name = tables.Column("name", verbose_name=_("Name"))
    image = tables.Column('image_name', verbose_name=_("Image Name"))
    zone = tables.Column('availability_zone',
                         verbose_name=_("Availability Zone"))
    status = tables.Column("status", verbose_name=_("Server Status"))
    addresses = tables.Column("addresses", verbose_name=_("Addresses"))
    visibility_enabled = tables.Column("visibility_enabled",
                                       verbose_name=_("Visibility Status"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")
        row_actions = (ToggleNetworkVisibility, NetworkVisibilityLink,)
        status_columns = ['status', 'visibility_enabled']
