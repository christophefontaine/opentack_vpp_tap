from django.utils.translation import ugettext_lazy as _

from horizon import tables
from openstack_dashboard.dashboards.project.instances \
    import tables as project_tables
from openstack_dashboard.api.nova import novaclient
import socket
import logging
LOG = logging.getLogger(__name__)


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
        
        if 'nsa' in instance.to_dict()['metadata']:
            self.visibility_enabled = (instance.to_dict()['metadata']['nsa'] == 'True')
        else:
            self.visibility_enabled = False
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
        kibana_ip = str(socket.gethostbyname(socket.gethostname()))
        kibana_port = '5601'
        if datum:
            instance_id = self.table.get_object_id(datum)
        # query should be something like :
        # network.visibility && 1bd8828e-3daf-439a-8484-0e1332bd6079
        url = "http://{kibana_ip}:{kibana_port}/app/kibana#/discover/network_visibility?_a=%28columns:!%28_source%29,filters:!%28%29,index:ceilometer,interval:auto,query:%28query_string:%28analyze_wildcard:!t,query:%27network.visibility%20%26%26%20{vm_id}%20%27%29%29,sort:!%28timestamp,desc%29%29&_g=%28filters:!%28%29,refreshInterval:%28display:%271%20day%27,pause:!f,section:3,value:86400000%29,time:%28from:now-1h,mode:quick,to:now%29%29".format(kibana_ip=kibana_ip, kibana_port=kibana_port, vm_id=instance_id or '')
        return url


class InstancesTable(tables.DataTable):
    tenant = tables.Column("tenant_name", verbose_name=_("Tenant"))
    name = tables.Column("name", verbose_name=_("Name"))
    image = tables.Column('image_name', verbose_name=_("Image Name"))
    zone = tables.Column('availability_zone',
                         verbose_name=_("Availability Zone"))
    status = tables.Column("status", verbose_name=_("Server Status"))
#    addresses = tables.Column("addresses", verbose_name=_("Addresses"))
    ip = tables.Column(project_tables.get_ips,
                       verbose_name=_("IP Address"),
                       attrs={'data-type': "ip"})
    visibility_enabled = tables.Column("visibility_enabled",
                                       verbose_name=_("Visibility Status"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")
        row_actions = (ToggleNetworkVisibility, NetworkVisibilityLink,)
        status_columns = ['status', 'visibility_enabled']
