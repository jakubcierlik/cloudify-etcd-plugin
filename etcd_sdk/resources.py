# Standard imports
import signal

# Local imports
from etcd_sdk.common import EtcdResource
from cloudify.exceptions import TimeoutException


# TODO: add support for lock, maybe members and alarms?
class EtcdKeyValuePair(EtcdResource):
    resource_type = 'keyvaluepair'

    def create(self, lease=None, prev_kv=False):
        self.logger.debug(
            'Creating (putting) etcd key-value pair with parameters: {}'
            .format(self.config)
        )
        key = self.config.get('key')
        value = self.config.get('value')
        # TODO: add support for fail_on_overwrite flag
        fail_on_overwrite = self.config.get('fail_on_overwrite')
        response = self.connection.put(
            key=key,
            value=value,
            lease=lease,
            prev_kv=prev_kv
            )
        self.logger.info(
            'Created key-value pair with result: {}'.format(response)
        )
        return key, value

    def list_all(self, sort_order=None, sort_target='key'):
        response = self.connection.get_all(
            sort_order=sort_order, sort_target=sort_target
        )
        self.logger.debug(
            'Listing all defined key-value pairs: {}'.format(response)
        )
        return response

    def get(self, key):
        self.logger.debug(
            'Attempting to get the value of: "{}"'.format(key)
        )
        response = self.connection.get(key)
        self.logger.debug(
            'Received value of: "{}": {}'.format(key, str(response))
        )
        return response

    def get_prefix(self, key_prefix, sort_order=None, sort_target='key'):
        self.logger.debug(
            'Attempting to get values of all keys with prefix: "{}"'
            .format(key_prefix)
        )
        response = self.connection.get_prefix(
            key_prefix, sort_order=sort_order, sort_target=sort_target
        )
        self.logger.debug(
            'Received values of all keys with prefix "{}": {}'
            .format(key_prefix, response)
        )
        return response

    def get_range(
        self, range_start, range_end, sort_order=None, sort_target='key'
    ):
        self.logger.debug(
            'Attempting to get values of all keys in range: {}-{}'
            .format(range_start, range_end)
        )
        response = self.connection.get_range(
            range_start,
            range_end,
            sort_order=sort_order,
            sort_target=sort_target
        )
        self.logger.debug(
            'Received values of all keys in range: {}-{}: {}'
            .format(range_start, range_end, response)
        )
        return response

    def create_lease(self, ttl, lease_id=None):
        """Create a new lease.
        All keys attached to this lease will be expired and deleted if
        the lease expires. A lease can be sent keep alive messages to
        refresh the ttl.
        """
        lease_id_str = 'ID: {}'.format(lease_id) if lease_id else 'random ID'
        self.logger.debug(
            'Attempting to create lease with {}'.format(lease_id_str)
        )
        response = self.connection.lease(ttl, lease_id=lease_id)
        self.config['lease'] = response
        self.logger.debug(
            'Created lease with result: {}'.format(response)
        )
        return response

    def revoke_lease(self, lease_id):
        self.logger.debug(
            'Attempting to revoke the lease: {}'.format(lease_id)
        )
        response = self.connection.revoke_lease(lease_id)
        self.logger.debug(
            'Revoked the lease with ID: {} with result: {}'
            .format(lease_id, response)
        )
        return response

    def refresh_lease(self, lease_obj):
        lease_obj.refresh()

    def delete(self, prev_kv=False, return_response=False):
        key = self.config.get('key')
        self.logger.debug(
            'Attempting to delete the key: {}'.format(key)
        )
        response = self.connection.delete(
            key, prev_kv=prev_kv, return_response=return_response
        )
        # TODO: add some check if the deletion was successful
        self.logger.debug(
            'Deleted key-value pair "{}" with result: {}'.format(key, response)
        )
        return response

    def delete_prefix(self, prefix):
        keys_with_prefix = self.get_prefix(prefix)
        self.logger.debug(
            'Attempting to delete all keys with prefix "{}". '
            'Keys to be deleted: {}'.format(prefix, keys_with_prefix)
        )
        response = self.connection.delete_prefix(prefix)
        # TODO: add some check if the deletion was successful
        self.logger.debug(
            'Deleted key-value pairs with prefix: "{}"'.format(prefix)
        )
        return response


class WatchKey(EtcdResource):
    resource_type = 'watchkey'
    default_timeout = 600  # seconds

    @staticmethod
    def handler(signum, frame):
        raise TimeoutException

    def watch(self):
        key = self.config.get('key')
        condition = self.config.get('condition')
        timeout = self.config.get('timeout', None) or self.default_timeout
        self.logger.debug(
            'Started watching key: {}. Expected value: {}'
            .format(key, condition)
        )
        events_iterator, cancel = self.connection.watch(key)
        if self.connection.get(key)[0] == condition:
            self.logger.debug(
                'Key: {0} already meets condition: {1}'.format(key, condition)
            )
        else:
            signal.signal(signal.SIGALRM, self.handler)
            signal.alarm(timeout)
            try:
                for event in events_iterator:
                    self.logger.debug(
                        'Event value: {}'.format(event.value.decode('utf-8'))
                    )
                    if event.value.decode('utf-8') == condition:
                        cancel()
            except TimeoutException:
                raise TimeoutException(
                    'Key: {0} - timeout {1} secs exceeded on condition: {2}'
                    .format(key, timeout, condition)
                )
            self.logger.debug(
                'Stopped watching key: {}'.format(key)
            )
        return True
