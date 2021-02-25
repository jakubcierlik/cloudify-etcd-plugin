# Standard Imports
import sys
import inspect

# Third party imports
import etcd3.exceptions
from cloudify import ctx as CloudifyContext
from cloudify.exceptions import NonRecoverableError
from cloudify.utils import exception_to_error_cause
from cloudify.constants import NODE_INSTANCE, RELATIONSHIP_INSTANCE

# Local imports
from etcd_plugin.constants import (
    RESOURCE_ID,
    ETCD_TYPE_PROPERTY,
    ETCD_NAME_PROPERTY,
    ETCD_EXTERNAL_RESOURCE,
    USE_EXTERNAL_RESOURCE_PROPERTY,
    CREATE_IF_MISSING_PROPERTY,
    CONDITIONALLY_CREATED,
    CLOUDIFY_CREATE_OPERATION,
    CLOUDIFY_DELETE_OPERATION,
    CLOUDIFY_NEW_NODE_OPERATIONS
)


# Help functions

def set_runtime_properties_from_resource(_ctx,
                                         etcd_resource):
    """
    Set etcd "type" & "name" as runtime properties for current cloudify
    node instance
    :param _ctx: Cloudify node instance which is could be an instance of
    RelationshipSubjectContext or CloudifyContext
    :param etcd_resource: etcd resource instance
    """
    if _ctx and etcd_resource:
        _ctx.instance.runtime_properties[
            ETCD_TYPE_PROPERTY] = etcd_resource.resource_type

        _ctx.instance.runtime_properties[
            ETCD_NAME_PROPERTY] = etcd_resource.name


def unset_runtime_properties_from_instance(_ctx):
    """
    Unset all runtime properties from node instance when delete operation
    task if finished
    :param _ctx: Cloudify node instance which is could be an instance of
    RelationshipSubjectContext or CloudifyContext
    """
    for key in list(_ctx.instance.runtime_properties.keys()):
        del _ctx.instance.runtime_properties[key]


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


def update_runtime_properties_for_operation_task(operation_name,
                                                 _ctx,
                                                 etcd_resource=None):
    """
    This method will update runtime properties for node instance based on
    the operation task being running
    :param str operation_name:
    :param _ctx: Cloudify node instance which is could be an instance of
    RelationshipSubjectContext or CloudifyContext
    :param etcd_resource: etcd resource instance
    """

    # Set runtime properties for "name" & "type" when current
    # operation is "create", so that they can be used later on
    if operation_name == CLOUDIFY_CREATE_OPERATION:
        set_runtime_properties_from_resource(_ctx,
                                             etcd_resource)
    # Clean all runtime properties for node instance when current operation
    # is delete
    elif operation_name == CLOUDIFY_DELETE_OPERATION:
        unset_runtime_properties_from_instance(_ctx)


def lookup_remote_resource(_ctx, etcd_resource):
    """
    This method will try to lookup etcd remote resource based on the
    instance type
    :param _ctx Cloudify node instance which is could be an instance of
    RelationshipSubjectContext or CloudifyContext
    :param etcd_resource: Instance derived from "EtcdResource",
    it could be "EtcdKeyValuePair" or "WatchKey" ..etc
    :return: etcd value stored remotely
    """

    try:
        # Get the remote resource
        remote_resource = etcd_resource.get(
            get_key_from_resource_config(_ctx)
        )
    except etcd3.exceptions.Etcd3Exception as error:
        _, _, tb = sys.exc_info()
        # If external resource does not exist then try to create it instead
        # of failed, when "create_if_missing" is set to "True"
        if is_create_if_missing(_ctx):
            _ctx.instance.runtime_properties[CONDITIONALLY_CREATED] = True
            etcd_resource.resource_id = None
            return None
        raise NonRecoverableError(
            'Failure while trying to request '
            'etcd API: {}'.format(error.message),
            causes=[exception_to_error_cause(error, tb)])
    return remote_resource


def is_external_resource(_ctx):
    """
    This method is to check if the current node is an external etcd
    resource or not
    :param _ctx Cloudify node instance which is could be an instance of
    RelationshipSubjectContext or CloudifyContext
    :return bool: Return boolean flag to indicate if it is external or not
    """
    return True if \
        _ctx.node.properties.get(USE_EXTERNAL_RESOURCE_PROPERTY) else False


def is_create_if_missing(_ctx):
    """
    This method is to check if the current node has a "create_if_missing"
    property in order to create resource even when "use_external_resource"
    is set to "True"
    resource or not
    :param _ctx Cloudify node instance which is could be an instance of
    RelationshipSubjectContext or CloudifyContext
    :return bool: Return boolean flag in order to decided if we should
    create external resource or not
    """
    return True if \
        _ctx.node.properties.get(CREATE_IF_MISSING_PROPERTY) else False


def is_external_relationship(_ctx):
    """
    This method is to check if both target & source nodes are external
    resources with "use_external_resource"
    :param _ctx: Cloudify context cloudify.context.CloudifyContext
    :return bool: Return boolean flag in order to decide if both resources
    are external
    """
    if is_external_resource(_ctx.source) and is_external_resource(_ctx.target):
        return True
    return False


def use_external_resource(_ctx,
                          etcd_resource,
                          existing_resource_handler=None,
                          **kwargs):
    """
    :param _ctx Cloudify node instance which is could be an instance of
    RelationshipSubjectContext or CloudifyContext
    :param etcd_resource: etcd resource instance
    :param existing_resource_handler: Callback handler that used to be
    called in order to execute custom operation when "use_external_resource" is
    enabled
    :param kwargs: Any extra param passed to the existing_resource_handler
    """
    # The cases when it is allowed to run operation tasks for resources
    # 1- When "use_external_resource=False"
    # 2- When "create_if_missing=True" and "use_external_resource=True"
    # 3- When "use_external_resource=True" and the current operations
    # are not included in the following operation list
    #   - "cloudify.interfaces.lifecycle.create"
    #   - "cloudify.interfaces.lifecycle.configure"
    #   - "cloudify.interfaces.lifecycle.start"
    #   - "cloudify.interfaces.lifecycle.stop"
    #   - "cloudify.interfaces.lifecycle.delete"
    #   - "cloudify.interfaces.validation.creation"

    # 4- When "use_external_resource=True" for (source|target) node node but
    # "use_external_resource=False" for (target|source) node for the
    # following relationship operations:
    #   - "cloudify.interfaces.relationship_lifecycle.preconfigure"
    #   - "cloudify.interfaces.relationship_lifecycle.postconfigure"
    #   - "cloudify.interfaces.relationship_lifecycle.establish"
    #   - "cloudify.interfaces.relationship_lifecycle.unlink"

    # Run custom operation When "existing_resource_handler" is not None,
    # so that it helps to validate or run that operation for external
    # existing resource in the following cases only:

    # 1- When "use_external_resource=True" for the following tasks:
    #   - "cloudify.interfaces.lifecycle.create"
    #   - "cloudify.interfaces.lifecycle.configure"
    #   - "cloudify.interfaces.lifecycle.start"
    #   - "cloudify.interfaces.lifecycle.stop"
    #   - "cloudify.interfaces.lifecycle.delete"
    #   - "cloudify.interfaces.validation.creation"

    # 2- When "use_external_resource=True" for both source & target node on
    # the for the following operations:
    #   - "cloudify.interfaces.relationship_lifecycle.preconfigure"
    #   - "cloudify.interfaces.relationship_lifecycle.postcofigure"
    #   - "cloudify.interfaces.relationship_lifecycle.establish"
    #   - "cloudify.interfaces.relationship_lifecycle.unlink"

    # Return None to indicate that this is the resource is not created and
    # we should continue and run operation node tasks
    if not is_external_resource(_ctx):
        return None

    CloudifyContext.logger.info(
        'Using external resource {0}'.format(RESOURCE_ID)
    )
    # Get the current operation name
    operation_name = get_current_operation()

    # Try to lookup remote resource
    remote_resource = lookup_remote_resource(_ctx, etcd_resource)
    if remote_resource:
        # Set external resource as runtime property for create operation
        set_external_resource(
            _ctx, etcd_resource, [CLOUDIFY_CREATE_OPERATION]
        )

    # Check if the current node instance is conditional created or not
    is_create = _ctx.instance.runtime_properties.get(CONDITIONALLY_CREATED)
    # Check if context type is "relationship-instance" and to check if both
    # target and source are not external
    is_not_external_rel = CloudifyContext.type == RELATIONSHIP_INSTANCE \
        and not is_external_relationship(CloudifyContext)

    if is_create or is_not_external_rel:
        return None

    if remote_resource:
        etcd_resource.resource_id = remote_resource.id
    # Just log message that we cannot delete resource since it is an
    # external resource
    if operation_name == CLOUDIFY_CREATE_OPERATION:
        _ctx.logger.info(
            'not creating resource {0}'
            ' since an external resource is being used'
            ''.format(remote_resource.name))
        _ctx.instance.runtime_properties[RESOURCE_ID] = remote_resource.id
        if hasattr(remote_resource, 'name') and remote_resource.name:
            etcd_resource.name = remote_resource.name
    # Just log message that we cannot delete resource since it is an
    # external resource
    elif operation_name == CLOUDIFY_DELETE_OPERATION:
        _ctx.logger.info(
            'not deleting resource {0}'
            ' since an external resource is being used'
            ''.format(remote_resource.name))

    # Check if we need to run custom operation for already existed
    # resource for operation task
    if existing_resource_handler:
        # We may need to send the "etcd_resource" to the
        # existing resource handler and in order to do that we may
        # need to check if the resource is already there or not
        func_args = inspect.getargspec(existing_resource_handler).args
        if 'etcd_resource' in func_args:
            kwargs['etcd_resource'] = etcd_resource

        existing_resource_handler(**kwargs)

    # Check which operations are allowed to execute when
    # "use_external_resource" is set to "True" and "node_type" is instance
    if CloudifyContext.type == NODE_INSTANCE \
            and allow_to_run_operation_for_external_node(operation_name):
        return None
    else:
        # Update runtime properties for operation create | delete operations
        update_runtime_properties_for_operation_task(operation_name,
                                                     _ctx,
                                                     etcd_resource)
        # Return instance of the external node
        return etcd_resource


def get_key_from_resource_config(ctx_node):
    """
    Get the key stored in resource config for the context
    :param ctx_node: This could be RelationshipSubjectContext
     or CloudifyContext instance depend if it is a normal relationship
     operation or node operation
    :return: Key name
    """
    return ctx_node.node.properties.get('resource_config').get('key')


def get_current_operation():
    """ Get the current task operation from current cloudify context
    :return str: Operation name
    """
    return CloudifyContext.operation.name


def allow_to_run_operation_for_external_node(operation_name):
    """
    This method to check if an a current operation is allowed for external
    node that has flag "use_external_resource" set "True"
    :param (str) operation_name: The cloudify operation name for node
    :return bool: Flag to indicate whether or not it is allowed to run
    operation for the external node
    """
    if operation_name not in CLOUDIFY_NEW_NODE_OPERATIONS:
        return True
    return False


def set_external_resource(ctx_node, resource, target_operations):
    """
    This method will set external resource as runtime property for node
    instance
    :param ctx_node: This could be RelationshipSubjectContext
     or CloudifyContext instance depend if it is a normal relationship
     operation or node operation
    :param resource:  Instance of etcd resource
    :param target_operations: Operations allowed to set "external_resource"
    runtime property
    """
    # Save the external resource as runtime property in the following
    # operations:
    # 1. cloudify.interfaces.lifecycle.create
    # 2. cloudify.interfaces.operations.update
    # 3. cloudify.interfaces.operations.update_project
    if is_external_resource(ctx_node):
        operation_name = get_current_operation()
        remote_resource = resource.get(
            get_key_from_resource_config(ctx_node)
        )
        if operation_name in target_operations:
            ctx_node.instance.runtime_properties[ETCD_EXTERNAL_RESOURCE] \
                = remote_resource


# Decorators

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
    to pass to the external resource  handler
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
