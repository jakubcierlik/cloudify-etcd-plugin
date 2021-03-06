# Local imports
from etcd_plugin.decorators import with_etcd_resource
from etcd_sdk.resources import WatchKey


@with_etcd_resource(WatchKey)
def watch(etcd_resource):
    """
    Create a watch for the particular key.
    :param etcd_resource: Instance of etcd watch key resource
    """
    etcd_resource.watch()


@with_etcd_resource(WatchKey)
def delete(etcd_resource):
    """
    Delete the watch key node.
    :param etcd_resource: Instance of etcd watch key resource
    """
    return
