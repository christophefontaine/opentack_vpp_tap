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
        instance.visibility_enabled = "True"
	novaclient(request).servers.set_meta_item(str(instance.id), 'nsa', "True")


class NetworkVisibilityDisableAction(tables.Action):
    name = 'networkvisibility_disable_action'
    verbose_name = 'Disable Monitoring'

    def single(self, table, request, object_id):
        instance = table.get_object_by_id(object_id)
        instance.visibility_enabled = "False"
	novaclient(request).servers.set_meta_item(str(instance.id), 'nsa', "False")


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
    visibility_enabled = tables.Column("visibility_enabled",
                                       verbose_name=_("Visibility Status"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")
        row_actions = (NetworkVisibilityEnableAction,
                       NetworkVisibilityDisableAction,
                       NetworkVisibilityLink,)
        status_columns = ['status', 'visibility_enabled']
