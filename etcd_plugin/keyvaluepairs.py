# Third party imports
from cloudify import ctx

# Local imports
from etcd_plugin.utils import with_etcd_resource
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
def create(etcd_resource):
    """
    Create key-value pairs and put it in etcd store
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
        key, value = etcd_key_value_pair.create()
        ctx.instance.runtime_properties[key] = value


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
