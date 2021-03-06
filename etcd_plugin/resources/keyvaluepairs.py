# Third party imports
from cloudify import ctx

# Local imports
from . import get_desired_value
from etcd_plugin.decorators import with_etcd_resource
from etcd_sdk.resources import EtcdKeyValuePair
from cloudify.exceptions import NonRecoverableError


def handle_external_keyvaluepairs(etcd_resource):
    """
    This method will check the current status for external resource when
    use_external_resource is set to "True"
    :param etcd_resource: Instance Of EtcdKeyValuePair in order to
    use it
    """
    for kvpair in etcd_resource.config:
        etcd_key = kvpair.get('kvpair').get('key')
        etcd_resource.get(etcd_key)


@with_etcd_resource(EtcdKeyValuePair,
                    existing_resource_handler=handle_external_keyvaluepairs
                    )
def create(etcd_resource, **kwargs):
    """
    Create key-value pairs and put it in etcd store
    :param etcd_resource: Instance of etcd key-value pairs resource
    :param kwargs: Configuration must be provided in kwargs or
    runtime_properties in order to release lock and and it
    is fail_on_overwrite
    """
    ctx.instance.runtime_properties['all_keys'] = \
        ctx.instance.runtime_properties.get('all_keys') or []
    etcd_resource.config = \
        get_desired_value(
            'all_keys',
            kwargs,
            ctx.instance.runtime_properties,
            {
                'all_keys': ctx.node.properties.get('resource_config')
            })
    for kvpair in etcd_resource.config:
        ctx.logger.info(
            'Loading kvpair: {0}'.format(kvpair)
        )
        if 'kvpair' not in kvpair:
            raise NonRecoverableError(
                "Key and value should be stored "
                "in an object under the key 'kvpair'!"
            )
        resource_config = kvpair.get('kvpair')
        fail_on_overwrite = kwargs.get('fail_on_overwrite')
        if fail_on_overwrite:
            resource_config['fail_on_overwrite'] = fail_on_overwrite
        etcd_key_value_pair = EtcdKeyValuePair(
            client_config=etcd_resource.client_config,
            resource_config=resource_config,
            logger=etcd_resource.logger
        )
        etcd_key_value_pair.create()
        ctx.instance.runtime_properties['all_keys'].append(
            kvpair.get('kvpair'))


@with_etcd_resource(EtcdKeyValuePair)
def delete(etcd_resource):
    """
    Delete the key-value pairs
    :param etcd_resource: Instance of etcd key-value pairs resource
    """
    for kvpair in etcd_resource.config:
        ctx.logger.info(
            'Loading kvpair: {0}'.format(kvpair)
        )
        if 'kvpair' not in kvpair:
            raise NonRecoverableError(
                "Key and value should be stored "
                "in an object under the key 'kvpair'!"
            )
        etcd_key_value_pair = EtcdKeyValuePair(
            client_config=etcd_resource.client_config,
            resource_config=kvpair.get('kvpair'),
            logger=etcd_resource.logger
        )
        etcd_key_value_pair.delete()
