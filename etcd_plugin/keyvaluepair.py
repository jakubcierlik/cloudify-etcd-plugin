# Third party imports
from cloudify import ctx

# Local imports
# from etcd_sdk.resources import EtcdKeyValuePair


def create(etcd_resource):
    """
    Create a key-value pair and put it in etcd store
    :param etcd_resource: Instance of etcd key-value pair resource
    """
    key, value = etcd_resource.create()
    ctx.instance.runtime_properties[key] = value


def delete(etcd_resource):
    """
    Delete the key-value pair
    :param etcd_resource: Instance of etcd key-value pair resource
    """
    etcd_resource.delete()
