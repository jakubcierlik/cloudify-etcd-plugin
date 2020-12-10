# Standard Imports
import sys

# Third party imports
from cloudify import ctx as CloudifyContext
from cloudify.exceptions import NonRecoverableError


# Help functions

def prepare_resource_instance(class_decl, _ctx, kwargs):
    """
    This method used to prepare and instantiate instance of etcd resource
    So that it can be used to make request to execute required operation
    :param class_decl: Class name of the resource instance we need to create
    :param _ctx: Cloudify node instance which is CloudifyContext
    :param kwargs: Some config contains data for etcd resource that
    could be provided via input task operation
    :return: Instance of etcd resource
    """
    def get_property_by_name(property_name):
        property_value = None
        if _ctx.node.properties.get(property_name):
            property_value = \
                _ctx.node.properties.get(property_name)

        if _ctx.instance.runtime_properties.get(property_name):
            if isinstance(property_value, dict):
                property_value.update(
                    _ctx.instance.runtime_properties.get(
                        property_name))
            else:
                property_value = \
                    _ctx.instance.runtime_properties.get(
                        property_name)

        if kwargs.get(property_name):
            kwargs_value = kwargs.pop(property_name)
            if isinstance(property_value, dict):
                property_value.update(kwargs_value)
            else:
                return kwargs_value
        return property_value

    client_config = get_property_by_name('client_config')
    resource_config = get_property_by_name('resource_config')

    # If this arg exists, user provide extra/optional configuration for
    # the defined node
    extra_resource_config = resource_config.pop('kwargs', None)
    if extra_resource_config:
        resource_config.update(extra_resource_config)

    resource = class_decl(client_config=client_config,
                          resource_config=resource_config,
                          logger=_ctx.logger)

    return resource


# Decorators

def with_etcd_resource(class_decl):
    """
    :param class_decl: This is a class for the etcd resource that need to
    be invoked
    :return: a wrapper object encapsulating the invoked function
    """
    def wrapper_outer(func):
        def wrapper_inner(**kwargs):
            # Get the context for the current task operation
            ctx_node = kwargs.pop('ctx', CloudifyContext)

            # Get the current operation name
            operation_name = ctx_node.operation.name
            try:
                # Prepare the etcd resource that need to execute the
                # current task operation
                resource = \
                    prepare_resource_instance(class_decl, ctx_node, kwargs)

                # run action
                kwargs['etcd_resource'] = resource
                func(**kwargs)
                # update_runtime_properties_for_operation_task(operation_name,
                #                                              ctx_node,
                #                                              resource)

            except Exception as errors:
                _, _, tb = sys.exc_info()
                raise NonRecoverableError(
                    'Failure while trying to run operation:'
                    '{0}: {1}'.format(operation_name, errors))
        return wrapper_inner
    return wrapper_outer
