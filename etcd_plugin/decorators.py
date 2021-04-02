# Standard Imports
import sys

# Third party imports
from cloudify import ctx as CloudifyContext
from cloudify.exceptions import NonRecoverableError, RecoverableError

# Local imports
from etcd_plugin.utils import (
    prepare_resource_instance,
    use_external_resource,
    update_runtime_properties_for_operation_task
)


def with_etcd_resource(class_decl,
                       existing_resource_handler=None,
                       **existing_resource_kwargs):
    """
    :param class_decl: This is a class for the etcd resource that need to
    be invoked
    :param existing_resource_handler: This is a method that handle any
    custom operation need to be done in case "use_external_resource" is set
    to true
    :param existing_resource_kwargs: This is an extra param that we may need
    to pass to the external resource handler
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

                if use_external_resource(ctx_node, resource,
                                         existing_resource_handler,
                                         **existing_resource_kwargs):
                    return

                # run action
                kwargs['etcd_resource'] = resource
                func(**kwargs)
                update_runtime_properties_for_operation_task(operation_name,
                                                             ctx_node,
                                                             resource)
            except RecoverableError as error:
                raise error
            except Exception as errors:
                _, _, tb = sys.exc_info()
                raise NonRecoverableError(
                    'Failure while trying to run operation:'
                    '{0}: {1}'.format(operation_name, errors))
        return wrapper_inner
    return wrapper_outer
