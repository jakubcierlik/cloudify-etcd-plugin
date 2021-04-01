# Standard imports
import signal

# Local imports
from etcd_sdk.common import EtcdResource
from cloudify.exceptions import (
    TimeoutException,
    RecoverableError,
    NonRecoverableError,
    CommandExecutionError,
)


class EtcdKeyValuePair(EtcdResource):
    resource_type = 'keyvaluepair'

    def create(self, lease=None, prev_kv=False):
        self.logger.debug(
            'Creating (putting) etcd key-value pair with parameters: {}'
            .format(self.config)
        )
        key = self.config.get('key')
        value = self.config.get('value')
        fail_on_overwrite = self.config.get('fail_on_overwrite')
        if fail_on_overwrite:
            existing_value, existing_kvmetadata = self.connection.get(key)
            if existing_kvmetadata:
                raise RecoverableError(
                    "fail_on_overwrite in config is enabled and value '{0}'"
                    " is already stored".format(str(existing_value))
                )
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
        fail_on_overwrite = self.config.get('fail_on_overwrite')
        if fail_on_overwrite:
            predelete_value, existing_kvmetadata = self.connection.get(key)
            if self.config.get('value') != str(predelete_value):
                return
            response = self.connection.delete(
                key, prev_kv=True, return_response=True
            )
            if not response.deleted:
                raise RecoverableError(
                    'Key: {0} delete unsuccessful'.format(key))
            deleted_value = response.prev_kvs[-1].value
            if deleted_value != str(predelete_value):
                raise CommandExecutionError(
                    'etcd3 delete key',
                    'Deleted another value ({0}) than expected ({1}) for'
                    ' key: {2}'.format(deleted_value, predelete_value, key)
                )
        else:
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


class EtcdLock(EtcdResource):
    resource_type = 'lock'
    default_ttl = 60  # seconds
    default_acquire_timeout = 10  # seconds

    def create(self):
        lock_name = self.config.get('lock_name') or self.config.get('name')
        ttl = self.config.get('ttl', None) or self.default_ttl
        acquire_timeout = self.config.get('acquire_timeout', None) \
            or self.default_acquire_timeout
        lock_obj = self.connection.lock(lock_name, ttl=ttl)
        recoverable_error = RecoverableError(
            'Failed to acquire lock: {}'
            .format(lock_obj.name)
        )
        self.logger.debug(
            'Acquiring lock "{}" with time-to-live: {} s'
            .format(lock_name, ttl)
        )
        try:
            if lock_obj.acquire(timeout=acquire_timeout):
                self.logger.debug(
                    'Acquired lock "{}" with time-to-live: {} s'
                    .format(lock_obj.name, lock_obj.ttl)
                )
                return lock_obj
            else:
                raise recoverable_error
        # lock_obj.acquire: handle tenacity wait gets an unexpected keyword
        # argument 'retry_state'
        except TypeError:
            raise recoverable_error

    def validate_lock_acquired(self):
        lock_name = self.config.get('lock_name') or self.config.get('name')
        key = self.config.get('key')
        lock_bytes_uuid = self.config.get('lock_bytes_uuid')
        value, _ = self.connection.get(key)
        if value != lock_bytes_uuid \
                or value is None:
            raise NonRecoverableError(
                'Lock "{}" not acquired.'.format(lock_name)
            )

    def refresh(self):
        lease_id = self.config.get('lock_lease_id')
        response = list(self.connection.refresh_lease(lease_id))
        if response:
            self.logger.debug(
                'Refreshed lock with lease ID: {}'.format(lease_id)
            )
        else:
            raise RecoverableError('Unable to refresh lock with lease ID: {}'
                                   .format(lease_id))

    def delete(self):
        lock_name = self.config.get('lock_name') or self.config.get('name')
        key = self.config.get('key')
        lock_bytes_uuid = self.config.get('lock_bytes_uuid')
        value, _ = self.connection.get(key)
        if value == lock_bytes_uuid:
            self.logger.debug(
                'Releasing lock: {}'.format(lock_name)
            )
            response = self.connection.delete(key)
            self.logger.debug(
                'Deleted lock "{}" with result: {}'.format(lock_name, response)
            )
            return response
        if value:
            self.logger.info(
                'Lock "{}" is not acquired, maybe another one is already'
                ' acquired. Release skipped.'.format(lock_name)
            )
            return False
        self.logger.info(
            'Lock "{}" not acquired. Release skipped.'.format(lock_name)
        )
        return False


class EtcdMember(EtcdResource):
    resource_type = 'member'

    def create(self):
        peer_urls = self.config.get('peer_urls')
        self.logger.debug(
            'Adding new member with peer URLs: {}'
            .format(peer_urls)
        )
        new_member = self.connection.add_member(peer_urls)
        self.logger.debug(
            'Added new member with peer URLs: {} and ID: {}'
            .format(new_member.peer_urls, new_member.id)
        )
        return new_member

    def list(self):
        members = self.connection.members
        self.logger.debug(
            'Listing all defined key-value pairs: {}'.format(members)
        )
        return members

    def update(self):
        member_id = self.config.get('member_id')
        peer_urls = self.config.get('peer_urls')
        self.logger.debug(
            'Updating member peer URLs: {} and ID: {}'
            .format(peer_urls, member_id)
        )
        self.connection.update_member(member_id, peer_urls)

    def disarm_alarms(self):
        member_id = self.config.get('member_id')
        if member_id == 'all':
            self.logger.debug(
                'Disarming all alarms from all members.'
            )
            response = self.connection.disarm_alarm(member_id=0)
            alarms_list = list(response)
        else:
            self.logger.debug(
                'Disarming all alarms from member: {}'
                .format(member_id)
            )
            response = self.connection.disarm_alarm(member_id)
            alarms_list = list(
                filter(
                    lambda x: x.member_id == member_id,
                    list(response)
                )
            )
        if alarms_list:
            raise RecoverableError('Some alarms still remaining.')

    def delete(self):
        member_id = self.config.get('member_id')
        self.logger.debug(
            'Removing member ID: {}'.format(member_id)
        )
        self.connection.remove_member(member_id)
