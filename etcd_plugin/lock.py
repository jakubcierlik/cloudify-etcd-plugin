# Third party imports
from cloudify import ctx
from uuid import UUID

# Local imports
from . import get_desired_value
from etcd_plugin.utils import with_etcd_resource
from etcd_sdk.resources import EtcdLock


@with_etcd_resource(EtcdLock)
def create(etcd_resource):
    """
    Create and acquire a etcd lock.
    :param etcd_resource: Instance of etcd lock resource
    """
    lock_obj = etcd_resource.create()
    ctx.instance.runtime_properties['lock_key'] = lock_obj.key
    ctx.instance.runtime_properties['lock_lease_id'] = lock_obj.lease.id
    ctx.instance.runtime_properties['lock_hex_uuid'] = \
        UUID(bytes=lock_obj.uuid).hex


@with_etcd_resource(EtcdLock)
def acquirement_validation(etcd_resource, **kwargs):
    """
    Validate that the etcd lock is currently acquired
    :param etcd_resource: Instance of etcd lock resource
    :param kwargs: Configuration must be provided in kwargs or
    runtime_properties in order to release lock and these configuration
    are lock_key and lock_hex_uuid
    """

    key = get_desired_value(
            'lock_key',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    lock_hex_uuid = get_desired_value(
            'lock_hex_uuid',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    lock_bytes_uuid = UUID(hex=lock_hex_uuid).bytes

    etcd_resource.validate_lock_acquired(key, lock_bytes_uuid)

    ctx.logger.debug(
        'OK: lock "{}" is acquired.'.format(etcd_resource.name)
    )


@with_etcd_resource(EtcdLock)
def refresh(etcd_resource, **kwargs):
    """
    Refresh the etcd lock
    :param etcd_resource: Instance of etcd lock resource
    :param kwargs: Configuration must be provided in kwargs or
    runtime_properties in order to release lock and it is lock_lease_id
    """
    lease_id = get_desired_value(
            'lock_lease_id',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    etcd_resource.refresh(lease_id)


@with_etcd_resource(EtcdLock)
def delete(etcd_resource, **kwargs):
    """
    Delete and release the etcd lock
    :param etcd_resource: Instance of etcd lock resource
    :param kwargs: Configuration must be provided in kwargs or
    runtime_properties in order to release lock and these configuration
    are lock_key and lock_hex_uuid
    """

    key = get_desired_value(
            'lock_key',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    lock_hex_uuid = get_desired_value(
            'lock_hex_uuid',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    lock_bytes_uuid = UUID(hex=lock_hex_uuid).bytes

    etcd_resource.delete(key, lock_bytes_uuid)
