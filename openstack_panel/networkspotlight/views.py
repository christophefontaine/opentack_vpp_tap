from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from horizon import exceptions
from horizon.tables import DataTableView
import tables

from openstack_dashboard import api

import logging
LOG = logging.getLogger(__name__)


class IndexView(DataTableView):
    template_name = 'admin/networkspotlight/index.html'
    page_title = 'Network Spotlight'
    table_class = tables.InstancesTable

    def get_data(self):
        instances = []
        try:
            tenants, has_more = api.keystone.tenant_list(self.request)
        except Exception:
            tenants = []
            msg = _('Unable to retrieve instance project information.')
            exceptions.handle(self.request, msg)

        try:
            instances, self._more = api.nova.server_list(
                self.request,
                all_tenants=True)
            # search_opts=search_opts,
        except Exception:
            self._more = False
            exceptions.handle(self.request,
                              _('Unable to retrieve instance list.'))

        try:
            flavors = api.nova.flavor_list(self.request)
        except Exception:
            # If fails to retrieve flavor list, creates an empty list.
            flavors = []

        full_flavors = SortedDict([(f.id, f) for f in flavors])
        tenant_dict = SortedDict([(t.id, t) for t in tenants])

        for instance in instances:
            flavor_id = instance.flavor["id"]
            if flavor_id in full_flavors:
                instance.full_flavor = full_flavors[flavor_id]
            tenant = tenant_dict.get(instance.tenant_id, None)
            instance.tenant_name = getattr(tenant, "name", None)
            if 'nsa' in instance.metadata:
                instance.visibility_enabled = instance.metadata['nsa']
            else:
                instance.visibility_enabled = False
        print instances
        return instances
