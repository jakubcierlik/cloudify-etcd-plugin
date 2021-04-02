# Third party imports
from cloudify import ctx

# Local imports
from . import get_desired_value
from etcd_plugin.decorators import with_etcd_resource
from etcd_sdk.resources import EtcdMember


@with_etcd_resource(EtcdMember)
def create(etcd_resource):
    """
    Create a etcd member.
    :param etcd_resource: Instance of etcd member resource
    """
    new_member = etcd_resource.create()
    ctx.instance.runtime_properties['member_id'] = new_member.id
    ctx.instance.runtime_properties['peer_urls'] = new_member.peer_urls


@with_etcd_resource(EtcdMember)
def delete(etcd_resource, **kwargs):
    """
    Delete the etcd member
    :param etcd_resource: Instance of etcd member resource
    :param kwargs: Configuration must be provided in kwargs or
    runtime_properties in order to release lock and these configuration
    are lock_key and lock_hex_uuid
    """

    etcd_resource.config['member_id'] = get_desired_value(
            'member_id',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    etcd_resource.delete()


@with_etcd_resource(EtcdMember)
def update(etcd_resource, **kwargs):
    """
    Update the etcd member
    :param etcd_resource: Instance of etcd member resource
    :param kwargs: Configuration must be provided in kwargs or
    runtime_properties in order to release lock and these configuration
    are lock_key and lock_hex_uuid
    """

    etcd_resource.config['member_id'] = get_desired_value(
            'member_id',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    etcd_resource.config['peer_urls'] = get_desired_value(
            'peer_urls',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    etcd_resource.update()


@with_etcd_resource(EtcdMember)
def disarm(etcd_resource, **kwargs):
    """
    Disarm alarms of the etcd member
    :param etcd_resource: Instance of etcd member resource
    :param kwargs: Configuration must be provided in kwargs or
    runtime_properties in order to release lock and these configuration
    are lock_key and lock_hex_uuid
    """

    etcd_resource.config['member_id'] = get_desired_value(
            'member_id',
            kwargs,
            ctx.instance.runtime_properties,
            {}
        )

    etcd_resource.disarm_alarms()
