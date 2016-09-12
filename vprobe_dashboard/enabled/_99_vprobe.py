# The slug of the panel to be added to HORIZON_CONFIG. Required.
# PANEL = 'network_spotlight_panel'
PANEL = 'vprobe'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'admin'
# The slug of the panel group the PANEL is associated with.
PANEL_GROUP = 'admin'

# Python panel class of the PANEL to be added.
ADD_PANEL = \
    'vprobe.panel.VProbe'
