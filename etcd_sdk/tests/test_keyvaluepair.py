# Standard imports
from collections import namedtuple
import mock

# Local imports
from etcd_sdk.tests import base
from etcd_sdk.resources import (
    EtcdKeyValuePair,
    WatchKey,
    EtcdLock,
    EtcdMember
)
from cloudify.exceptions import (
    TimeoutException,
    RecoverableError,
    NonRecoverableError,
)


class KeyValuePairTestCase(base.EtcdSDKTestBase):
    def setUp(self):
        super(KeyValuePairTestCase, self).setUp()
        self.fake_client = self.generate_fake_etcd_connection('keyvaluepair')
        self.keyvaluepair_instance = EtcdKeyValuePair(
            client_config=self.client_config,
            logger=mock.MagicMock()
        )
        self.keyvaluepair_instance.connection = self.connection

    def test_create_keyvaluepair(self):
        config = {
            'key': b'test_key',
            'value': b'test_value',
        }

        Lease = namedtuple('Lease', 'id ttl')
        lease = Lease(1234L, 10L)

        self.keyvaluepair_instance.config = config
        self.fake_client.put = mock.MagicMock()

        returned_key, returned_value = \
            self.keyvaluepair_instance.create(lease=lease, prev_kv=True)

        self.fake_client.put.assert_called_with(
            key='test_key',
            value='test_value',
            lease=Lease(1234L, 10L),
            prev_kv=True
        )
        self.assertEqual(returned_key, 'test_key')
        self.assertEqual(returned_value, 'test_value')

    def test_protect_overwrite_keyvaluepair(self):
        config = {
            'key': b'test_key',
            'value': b'test_value',
            'fail_on_overwrite': True,
        }

        Lease = namedtuple('Lease', 'id ttl')
        lease = Lease(1234L, 10L)
        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'previous_value'

        self.keyvaluepair_instance.config = config

        self.fake_client.get = mock.MagicMock(return_value=(value, metadata))
        self.fake_client.put = mock.MagicMock()

        with self.assertRaises(RecoverableError):
            self.keyvaluepair_instance.create(lease=lease, prev_kv=True)

    def test_get_keyvaluepair(self):
        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'test_value'

        self.fake_client.get = mock.MagicMock(return_value=(value, metadata))

        response_value, response_metadata = \
            self.keyvaluepair_instance.get('test_key')

        self.assertEqual(response_value, value)
        self.assertEqual(response_metadata.version, 1)

    def test_list_all_keyvaluepairs(self):
        keyvaluepair_list = [
            (b'test_value1', {'key': b'test_key1'}),
            (b'test_value2', {'key': b'test_key2'}),
        ]
        self.fake_client.get_all = \
            mock.MagicMock(return_value=keyvaluepair_list)

        response = self.keyvaluepair_instance.list_all(
            sort_order='ascend',
            sort_target='create'
        )

        self.fake_client.get_all.assert_called_with(
            sort_order='ascend',
            sort_target='create'
        )
        self.assertEqual(len(response), 2)

    def test_get_prefix_keyvaluepairs(self):
        keyvaluepair_list = [
            (b'test_value1', {'key': b'test_key1'}),
            (b'test_value2', {'key': b'test_key2'}),
        ]

        self.fake_client.get_prefix = \
            mock.MagicMock(return_value=keyvaluepair_list)

        response = self.keyvaluepair_instance.get_prefix(
            'test_key',
            sort_order='descend',
            sort_target='version'
        )

        self.fake_client.get_prefix.assert_called_with(
            'test_key',
            sort_order='descend',
            sort_target='version'
        )
        self.assertEqual(len(response), 2)

    def test_get_range_keyvaluepairs(self):
        keyvaluepair_list = [
            (b'test_value1', {'key': b'test_key1'}),
            (b'test_value2', {'key': b'test_key2'}),
            (b'test_value3', {'key': b'test_key3'}),
            (b'test_value4', {'key': b'test_key4'}),
        ]

        self.fake_client.get_range = \
            mock.MagicMock(return_value=keyvaluepair_list)

        response = self.keyvaluepair_instance.get_range(
            'test_key1',
            'test_key5',
            sort_order='descend',
            sort_target='mod'
        )

        self.fake_client.get_range.assert_called_with(
            'test_key1',
            'test_key5',
            sort_order='descend',
            sort_target='mod'
        )
        self.assertEqual(len(response), 4)

    def test_create_lease(self):
        self.keyvaluepair_instance.config = dict()

        Response = namedtuple('Response', 'id ttl')
        response = Response(1234L, 10L)

        self.fake_client.lease = mock.MagicMock(return_value=response)

        response = self.keyvaluepair_instance.create_lease(10)
        self.assertEqual(response.id, 1234L)
        self.assertEqual(response.ttl, 10L)

    def test_revoke_lease(self):
        self.fake_client.revoke_lease = mock.MagicMock()

        self.keyvaluepair_instance.revoke_lease(1234L)

        self.fake_client.revoke_lease.assert_called_with(1234L)

    def test_refresh_lease(self):
        lease = mock.MagicMock()

        self.keyvaluepair_instance.refresh_lease(lease)

        lease.refresh.assert_called()

    def test_delete_keyvaluepair(self):
        config = {
            'key': b'test_key',
            'value': b'test_value',
        }
        self.keyvaluepair_instance.config = config
        self.fake_client.delete = mock.MagicMock(return_value=True)

        response = self.keyvaluepair_instance.delete(prev_kv=True,
                                                     return_response=True)

        self.fake_client.delete.assert_called_with('test_key',
                                                   prev_kv=True,
                                                   return_response=True)
        self.assertTrue(response)

    def test_delete_prefix(self):
        keyvaluepair_list = [
            (b'test_value1', {'key': b'test_key1'}),
            (b'test_value2', {'key': b'test_key2'}),
            (b'test_value3', {'key': b'test_key3'}),
            (b'test_value4', {'key': b'test_key4'}),
        ]

        Header = namedtuple('Header', 'revision')
        Response = namedtuple('Response', 'header deleted')
        response = Response(Header(2), 4L)

        self.fake_client.get_prefix = \
            mock.MagicMock(return_value=keyvaluepair_list)
        self.fake_client.delete_prefix = mock.MagicMock(return_value=response)

        response = self.keyvaluepair_instance.delete_prefix('test_key')

        self.assertEqual(response.deleted, 4L)


class WatchKeyTestCase(base.EtcdSDKTestBase):
    def setUp(self):
        super(WatchKeyTestCase, self).setUp()
        self.fake_client = self.generate_fake_etcd_connection('watchkey')
        self.watchkey_instance = WatchKey(
            client_config=self.client_config,
            logger=mock.MagicMock()
        )
        self.watchkey_instance.connection = self.connection

    def test_watch_cancelled(self):
        config = {
            'key': b'test_key',
            'condition': b'test_value',
        }

        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'foo'

        Event = namedtuple('Event', 'value')
        events_iterator = [
            Event('bar1'),
            Event('bar2'),
            Event('test_value'),
        ].__iter__()
        cancel_func = mock.MagicMock()

        self.watchkey_instance.config = config

        self.fake_client.get = mock.MagicMock(return_value=(value, metadata))
        self.fake_client.watch = mock.MagicMock(
            return_value=(events_iterator, cancel_func)
        )

        returned = self.watchkey_instance.watch()

        self.assertTrue(returned)
        cancel_func.assert_called_once()

    def test_watch_already_expected_value(self):
        config = {
            'key': b'test_key',
            'condition': b'test_value',
        }

        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'test_value'

        Event = namedtuple('Event', 'value')
        events_iterator = [
            Event('bar1'),
            Event('bar2'),
            Event('test_value'),
        ].__iter__()
        cancel_func = None  # expected not to be called

        self.watchkey_instance.config = config

        self.fake_client.get = mock.MagicMock(return_value=(value, metadata))
        self.fake_client.watch = mock.MagicMock(
            return_value=(events_iterator, cancel_func)
        )

        returned = self.watchkey_instance.watch()

        self.assertTrue(returned)

    def test_watch_timeout(self):
        config = {
            'key': b'test_key',
            'condition': b'test_value',
            'timeout': 1  # second
        }

        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'foo'

        events_num = 999999  # repeats that loop processing exceeds 1 sec
        Event = namedtuple('Event', 'value')
        events_iterator = ([Event('bar')] * events_num).__iter__()
        cancel_func = mock.MagicMock()

        self.watchkey_instance.config = config

        self.fake_client.get = mock.MagicMock(return_value=(value, metadata))
        self.fake_client.watch = mock.MagicMock(
            return_value=(events_iterator, cancel_func)
        )

        with self.assertRaises(TimeoutException):
            self.watchkey_instance.watch()


class LockTestCase(base.EtcdSDKTestBase):
    def setUp(self):
        super(LockTestCase, self).setUp()
        self.fake_client = self.generate_fake_etcd_connection('lock')
        self.lock_instance = EtcdLock(
            client_config=self.client_config,
            logger=mock.MagicMock()
        )
        self.lock_instance.connection = self.connection

    def test_create_lock(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
        }

        self.lock_instance.config = config

        Lock = namedtuple('Lock', 'name ttl acquire')
        acquire_method = mock.MagicMock(return_value=True)
        lock = Lock(name='test_lock',
                    ttl=600,
                    acquire=acquire_method)
        self.fake_client.lock = mock.MagicMock(return_value=lock)

        lock_obj = self.lock_instance.create()

        self.assertIsNotNone(lock_obj)
        acquire_method.assert_called()

    def test_create_cannot_acquire(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
        }

        self.lock_instance.config = config

        Lock = namedtuple('Lock', 'name ttl acquire')
        acquire_method = mock.MagicMock(return_value=False)
        lock = Lock(name='test_lock',
                    ttl=600,
                    acquire=acquire_method)
        self.fake_client.lock = mock.MagicMock(return_value=lock)

        with self.assertRaises(RecoverableError):
            self.lock_instance.create()
        acquire_method.assert_called()

    def test_validate_acquired(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
            'key': '/locks/test_lock',
            'lock_bytes_uuid':
                '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5',
        }

        self.lock_instance.config = config

        uuid_bytes = '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5'
        self.fake_client.get = mock.MagicMock(return_value=(uuid_bytes, None))

        self.lock_instance.validate_lock_acquired()

    def test_validate_not_acquired(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
            'key': '/locks/test_lock',
            'lock_bytes_uuid':
                '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5',
        }

        self.lock_instance.config = config

        self.fake_client.get = mock.MagicMock(return_value=(None, None))

        with self.assertRaises(NonRecoverableError):
            self.lock_instance.validate_lock_acquired()

    def test_validate_another_acquired(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
            'key': '/locks/test_lock',
            'lock_bytes_uuid':
                '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5',
        }

        self.lock_instance.config = config

        another_uuid_bytes = \
            'Q\xae\x91Z\x8dN\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5'
        self.fake_client.get = mock.MagicMock(
            return_value=(another_uuid_bytes, None))

        with self.assertRaises(NonRecoverableError):
            self.lock_instance.validate_lock_acquired()

    def test_refresh(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
            'lock_lease_id': 7668636638277611120L,
        }

        self.lock_instance.config = config
        LeaseKeepAliveResponse = namedtuple('LeaseKeepAliveResponse', 'ID')
        response = [LeaseKeepAliveResponse(7668636638277611120L)]
        self.fake_client.refresh_lease = mock.MagicMock(return_value=response)

        self.lock_instance.refresh()

        self.fake_client.refresh_lease.assert_called_with(7668636638277611120L)

    def test_delete(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
            'key': '/locks/test_lock',
            'lock_bytes_uuid':
                '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5',
        }

        self.lock_instance.config = config

        uuid_bytes = '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5'
        self.fake_client.get = mock.MagicMock(return_value=(uuid_bytes, None))
        self.fake_client.delete = mock.MagicMock(return_value=True)

        response = self.lock_instance.delete()

        self.assertTrue(response)
        self.fake_client.delete.assert_called_with('/locks/test_lock')

    def test_delete_not_acquired(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
            'key': '/locks/test_lock',
            'lock_bytes_uuid':
                '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5',
        }

        self.lock_instance.config = config

        self.fake_client.get = mock.MagicMock(return_value=(None, None))
        self.fake_client.delete = mock.MagicMock(return_value=True)

        response = self.lock_instance.delete()

        self.assertFalse(response)

    def test_delete_another_acquirement(self):
        config = {
            'lock_name': b'test_lock',
            'ttl': 600,
            'key': '/locks/test_lock',
            'lock_bytes_uuid':
                '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5',
        }

        self.lock_instance.config = config

        another_uuid_bytes = \
            'Q\xae\x91Z\x8dN\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5'
        self.fake_client.get = mock.MagicMock(
            return_value=(another_uuid_bytes, None))
        self.fake_client.delete = mock.MagicMock(return_value=True)

        response = self.lock_instance.delete()

        self.assertFalse(response)
        # any modification may exhibit undefined behavior
        self.fake_client.delete.assert_not_called()


class MemberTestCase(base.EtcdSDKTestBase):
    def setUp(self):
        super(MemberTestCase, self).setUp()
        self.fake_client = self.generate_fake_etcd_connection('member')
        self.member_instance = EtcdMember(
            client_config=self.client_config,
            logger=mock.MagicMock()
        )
        self.member_instance.connection = self.connection

    def test_create(self):
        config = {
            'name': b'test_member',
            'peer_urls': ['http://127.0.0.1:2380'],
        }

        self.member_instance.config = config

        Member = namedtuple('Member', 'id peer_urls')
        member = Member(10501334649042878790, ['http://127.0.0.1:2380'])
        self.fake_client.add_member = mock.MagicMock(return_value=member)

        new_member = self.member_instance.create()

        self.assertEquals(new_member.id, 10501334649042878790)
        self.assertEquals(new_member.peer_urls, ['http://127.0.0.1:2380'])

    def test_update(self):
        config = {
            'name': b'test_member',
            'member_id': 18129864113152051069,
            'peer_urls': ['http://127.0.0.1:2380'],
        }

        self.member_instance.config = config
        self.fake_client.update_member = mock.MagicMock()

        self.member_instance.update()

        self.fake_client.update_member.assert_called_with(
            18129864113152051069,
            ['http://127.0.0.1:2380']
        )

    def test_list(self):
        config = {
            'name': b'test_member',
        }

        self.member_instance.config = config

        Member = namedtuple('Member', 'id peer_urls')
        member1 = Member(10501334649042878790, ['http://10.0.0.10:2380'])
        member2 = Member(10501334649042878791, ['http://10.0.0.20:2380'])
        self.fake_client.members = [member1, member2]
        expected_members = [member1, member2]

        response = self.member_instance.list()

        self.assertEquals(response, expected_members)

    def test_disarm_member(self):
        config = {
            'name': b'test_member',
            'member_id': 18129864113152051069,
        }

        self.member_instance.config = config
        Alarm = namedtuple('Alarm', 'alarm_type member_id')
        alarms = [Alarm(1, 18129864113152051070L)]
        self.fake_client.disarm_alarm = mock.MagicMock(return_value=alarms)

        self.member_instance.disarm_alarms()

        self.fake_client.disarm_alarm \
            .assert_called_with(18129864113152051069)

    def test_disarm_all(self):
        config = {
            'name': b'test_member',
            'member_id': 'all',
        }

        self.member_instance.config = config
        alarms = []
        self.fake_client.disarm_alarm = mock.MagicMock(return_value=alarms)

        self.member_instance.disarm_alarms()

        self.fake_client.disarm_alarm \
            .assert_called_with(member_id=0)

    def test_not_all_disarmed(self):
        config = {
            'name': b'test_member',
            'member_id': 'all',
        }

        self.member_instance.config = config
        Alarm = namedtuple('Alarm', 'alarm_type member_id')
        alarms = [Alarm(1, 18129864113152051070L)]
        self.fake_client.disarm_alarm = mock.MagicMock(return_value=alarms)

        with self.assertRaises(RecoverableError):
            self.member_instance.disarm_alarms()

        self.fake_client.disarm_alarm \
            .assert_called_with(member_id=0)

    def test_delete(self):
        config = {
            'name': b'test_member',
            'member_id': 18129864113152051069,
        }

        self.member_instance.config = config
        self.fake_client.remove_member = mock.MagicMock()

        self.member_instance.delete()

        self.fake_client.remove_member \
            .assert_called_with(18129864113152051069)
