# cloudify-etcd-plugin

A Cloudify Plugin interacting with etcd.

## Usage
Node types:
- cloudify.nodes.etcd.**KeyValuePair**
  
  Create/delete etcd key-value pair.
- cloudify.nodes.etcd.**KeyValuePairs**
  
  Create/delete a list of _kvpair_ entries (see _examples/simple-list-blueprint/blueprint.yaml_).
- cloudify.nodes.etcd.**WatchKey**

  Watch value of etcd key. Succeeds when it matches _condition_ or fails on _timeout_ (default 600 secs).
- cloudify.nodes.etcd.**Lock**
  
  Create and acquire or delete and release etcd lock, applicable for distributed operations. Additional operations _acquirement_validation_ and _refresh_ are available (see usage in _examples/validate-lock-blueprint/blueprint.yaml_).
- cloudify.nodes.etcd.**Member**
  
  Create/update/delete member from etcd cluster, disarm alarm raised by one member or all members.

##Runtime properties:
####KeyValuePair

| key name   | value type |
| ---------- | ---------- |
| key        | string     |
| value      | string     |

####KeyValuePairs

| key name      | sub-key name      | value type |
| ------------- | ----------------- | ---------- |
| all_keys      | fail_on_overwrite | boolean    |
| all_keys      | key               | string     |
| all_keys      | value             | string     |

####WatchKey
no runtime properties

####Lock

| key name      | value type |
| ------------- | ---------- |
| lock_key      | string     |
| lock_lease_id | long       |
| lock_hex_uuid | string     |

####Member

| key name  | value type      |
| --------- | --------------- |
| member_id | long            |
| peer_urls | list of strings |

# Requirements
etcd3 Python Library

# Examples
Blueprints with etcd are located in examples directory.
For other official blueprint examples using this Cloudify plugin, please see [Cloudify Community Blueprints Examples](https://github.com/cloudify-community/blueprint-examples/).
