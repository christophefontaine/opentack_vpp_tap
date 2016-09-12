VPROBE_DASH_DIR=$(cd $(dirname $BASH_SOURCE)/.. && pwd)

function install_vprobe_dashboard {
    setup_develop ${VPROBE_DASH_DIR}
}

function install_vprobe_agentd {
    pushd vprobe_agentd
    sudo python setup.py install
    popd
}

function configure_vprobe_dashboard {
    cp -a ${VPROBE_DASH_DIR}/vprobe_dashboard/enabled/* ${DEST}/horizon/openstack_dashboard/local/enabled/
    # NOTE: If locale directory does not exist, compilemessages will fail,
    # so check for an existence of locale directory is required.
    if [ -d ${VPROBE_DASH_DIR}/vprobe_dashboard/locale ]; then
        (cd ${VPROBE_DASH_DIR}/vprobe_dashboard; DJANGO_SETTINGS_MODULE=openstack_dashboard.settings ../manage.py compilemessages)
    fi
}

# check for service enabled
if is_service_enabled vprobe_dashboard; then

    if [[ "$1" == "stack" && "$2" == "pre-install"  ]]; then
        # Set up system services
        # no-op
        :

    elif [[ "$1" == "stack" && "$2" == "install"  ]]; then
        # Perform installation of service source
        echo_summary "Installing vprobe Dashboard"
        install_vprobe_dashboard

    elif [[ "$1" == "stack" && "$2" == "post-config"  ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring vprobe Dashboard"
        configure_vprobe_dashboard

    elif [[ "$1" == "stack" && "$2" == "extra"  ]]; then
        # Initialize and start the app-catalog-ui service
        # no-op
        run_process vprobe-agentd "vprobe_agentd"
    fi

    if [[ "$1" == "unstack"  ]]; then
        # Shut down app-catalog-ui services
        # no-op
        :
    fi

    if [[ "$1" == "clean"  ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi
