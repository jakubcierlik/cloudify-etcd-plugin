# Third party imports
from cloudify import ctx

# Local imports
from etcd_plugin.utils import with_etcd_resource
from etcd_sdk.resources import EtcdKeyValuePair


def handle_external_keyvaluepair(etcd_resource):
    """
    This method will check the current status for external resource when
    use_external_resource is set to "True"
    :param etcd_resource: Instance Of EtcdKeyValuePair in order to
    use it
    """
    etcd_key = etcd_resource.config.get('key')
    etcd_resource.get(etcd_key)


@with_etcd_resource(EtcdKeyValuePair,
                    existing_resource_handler=handle_external_keyvaluepair)
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
