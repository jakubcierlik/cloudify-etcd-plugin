# Third party imports
from cloudify import ctx

# Local imports
from etcd_plugin.utils import with_etcd_resource
from etcd_sdk.resources import EtcdKeyValuePair


@with_etcd_resource(EtcdKeyValuePair)
def create(etcd_resource):
    """
    Create a key-value pair and put it in etcd store
    :param etcd_resource: Instance of etcd key-value pair resource
    """
    key, value = etcd_resource.create()
    ctx.instance.runtime_properties[key] = value


@with_etcd_resource(EtcdKeyValuePair)
def delete(etcd_resource):
    """
    Delete the key-value pair
    :param etcd_resource: Instance of etcd key-value pair resource
    """
    etcd_resource.delete()
