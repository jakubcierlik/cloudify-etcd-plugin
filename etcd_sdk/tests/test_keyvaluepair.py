# Standard imports
from collections import namedtuple
import mock

# Local imports
from etcd_sdk.tests import base
from etcd_sdk.resources import EtcdKeyValuePair, WatchKey


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

        Event = namedtuple('Event', 'value')
        events_iterator = [
                Event('bar1'),
                Event('bar2'),
                Event('test_value'),
        ].__iter__()
        cancel_func = mock.MagicMock()

        self.watchkey_instance.config = config
        self.fake_client.watch = mock.MagicMock(
                return_value=(events_iterator, cancel_func)
        )

        returned = self.watchkey_instance.watch()

        self.assertTrue(returned)
        cancel_func.assert_called_once()
