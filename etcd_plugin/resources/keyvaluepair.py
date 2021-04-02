# Third party imports
from cloudify import ctx

# Local imports
from . import get_desired_value
from etcd_plugin.decorators import with_etcd_resource
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
def create(etcd_resource, **kwargs):
    """
    Create a key-value pair and put it in etcd store
    :param etcd_resource: Instance of etcd key-value pair resource
    """
    etcd_resource.config['key'] = \
        get_desired_value(
            'key',
            kwargs,
            ctx.instance.runtime_properties,
            ctx.node.properties.get('resource_config'))

    etcd_resource.config['value'] = \
        get_desired_value(
            'value',
            kwargs,
            ctx.instance.runtime_properties,
            ctx.node.properties.get('resource_config'))

    etcd_resource.config['fail_on_overwrite'] = \
        get_desired_value(
            'fail_on_overwrite',
            kwargs,
            ctx.instance.runtime_properties,
            ctx.node.properties.get('resource_config'))

    key, value = etcd_resource.create()
    ctx.instance.runtime_properties['key'] = key
    ctx.instance.runtime_properties['value'] = value


@with_etcd_resource(EtcdKeyValuePair)
def delete(etcd_resource):
    """
    Delete the key-value pair
    :param etcd_resource: Instance of etcd key-value pair resource
    """
    etcd_resource.delete()
