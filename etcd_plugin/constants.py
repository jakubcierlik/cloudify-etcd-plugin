# Runtime properties keys
RESOURCE_ID = 'id'
ETCD_TYPE_PROPERTY = 'type'
ETCD_NAME_PROPERTY = 'name'
ETCD_EXTERNAL_RESOURCE = 'external_resource'
USE_EXTERNAL_RESOURCE_PROPERTY = 'use_external_resource'
CREATE_IF_MISSING_PROPERTY = 'create_if_missing'
CONDITIONALLY_CREATED = 'conditionally_created'

# General constants
CLOUDIFY_CREATE_OPERATION = 'cloudify.interfaces.lifecycle.create'
CLOUDIFY_CONFIGURE_OPERATION = 'cloudify.interfaces.lifecycle.configure'
CLOUDIFY_START_OPERATION = 'cloudify.interfaces.lifecycle.start'
CLOUDIFY_STOP_OPERATION = 'cloudify.interfaces.lifecycle.stop'
CLOUDIFY_DELETE_OPERATION = 'cloudify.interfaces.lifecycle.delete'
CLOUDIFY_CREATE_VALIDATION = 'cloudify.interfaces.validation.creation'
CLOUDIFY_NEW_NODE_OPERATIONS = [CLOUDIFY_CREATE_OPERATION,
                                CLOUDIFY_CONFIGURE_OPERATION,
                                CLOUDIFY_START_OPERATION,
                                CLOUDIFY_STOP_OPERATION,
                                CLOUDIFY_DELETE_OPERATION,
                                CLOUDIFY_CREATE_VALIDATION]
