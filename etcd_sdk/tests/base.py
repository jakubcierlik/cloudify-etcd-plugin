# Standard imports
import unittest
import mock

# Third party imports
import etcd3.exceptions as exceptions


class EtcdSDKTestBase(unittest.TestCase):

    def setUp(self):
        super(EtcdSDKTestBase, self).setUp()
        self.connection = mock.patch('etcd3.client', mock.MagicMock())

    def tearDown(self):
        super(EtcdSDKTestBase, self).tearDown()

    def get_etcd_connections(self):
        return {
            'keyvaluepair': self._fake_keyvaluepair,
            'watchkey': self._fake_watchkey,
            'lock': self._fake_lock
        }

    @property
    def client_config(self):
        return {}

    def _gen_etcd_sdk_error(self, message='SomeThingIsGoingWrong'):
        return mock.MagicMock(
            side_effect=exceptions.PreconditionFailedError())

    def generate_fake_etcd_connection(self, service_type):
        return self.get_etcd_connections()[service_type]()

    def _fake_keyvaluepair(self):
        self.connection.put = self._gen_etcd_sdk_error()
        self.connection.get_all = self._gen_etcd_sdk_error()
        self.connection.get = self._gen_etcd_sdk_error()
        self.connection.get_prefix = self._gen_etcd_sdk_error()
        self.connection.get_range = self._gen_etcd_sdk_error()
        self.connection.lease = self._gen_etcd_sdk_error()
        self.connection.revoke_lease = self._gen_etcd_sdk_error()
        self.connection.delete = self._gen_etcd_sdk_error()
        self.connection.delete_prefix = self._gen_etcd_sdk_error()
        return self.connection

    def _fake_watchkey(self):
        self.connection.watch = self._gen_etcd_sdk_error()
        return self.connection

    def _fake_lock(self):
        self.connection.lock = self._gen_etcd_sdk_error()
        return self.connection
