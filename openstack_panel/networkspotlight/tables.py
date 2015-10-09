from django.utils.translation import ugettext_lazy as _

from horizon import tables
from openstack_dashboard.api.nova import novaclient
import logging
LOG = logging.getLogger(__name__)


class NetworkVisibilityToggleAction(tables.Action):
    name = 'networkvisibility_toggle_action'
    verbose_name = 'Toggle'

    def single(self, table, request, object_id):
        LOG.info(request)
        instance = table.get_object_by_id(object_id)
        LOG.info(instance.visibility_enabled)
        if instance.visibility_enabled == "True":
            instance.visibility_enabled = "False"
        else:
            instance.visibility_enabled = "True"
        LOG.info(instance.visibility_enabled)
	novaclient(request).servers.set_meta_item(str(instance.id), 'nsa', instance.visibility_enabled)


class InstancesTable(tables.DataTable):
    tenant = tables.Column("tenant_name", verbose_name=_("Tenant"))
    name = tables.Column("name", verbose_name=_("Name"))
    image = tables.Column('image_name', verbose_name=_("Image Name"))
    zone = tables.Column('availability_zone',
                         verbose_name=_("Availability Zone"))
    status = tables.Column("status", verbose_name=_("Status"))
    visibility_enabled = tables.Column("visibility_enabled",
                                       verbose_name=_("Visibility Status"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")
        row_actions = (NetworkVisibilityToggleAction,)
        status_columns = ['status', 'visibility_enabled']
