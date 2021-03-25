# Third party imports
from collections import namedtuple
import mock

# Local imports
from etcd_plugin.tests.base import EtcdTestBase
from etcd_plugin import lock
from cloudify.exceptions import NonRecoverableError


@mock.patch('etcd3.client')
class LockTestCase(EtcdTestBase):

    def setUp(self):
        super(LockTestCase, self).setUp()

    @property
    def resource_config(self):
        return {
            'lock_name': 'test_lock',
            'ttl': 600
        }

    def test_create(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='LockTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create')
        Lock = namedtuple('Lock', 'name ttl key uuid acquire')
        acquire_method = mock.MagicMock(return_value=True)
        lock_obj = Lock(
            name='test_lock',
            ttl=600,
            key='/locks/test_lock',
            uuid='%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5',
            acquire=acquire_method
        )
        mock_connection().lock = mock.MagicMock(return_value=lock_obj)

        # act
        lock.create(etcd_resource=None)

        # assert
        self.assertEqual(self._ctx.instance.runtime_properties['lock_key'],
                         '/locks/test_lock')
        self.assertIsInstance(
            self._ctx.instance.runtime_properties['lock_hex_uuid'], str)
        acquire_method.assert_called()

    def test_delete(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='LockTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        bytes_uuid = '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5'
        self._ctx.instance.runtime_properties['lock_key'] = '/locks/test_lock'
        self._ctx.instance.runtime_properties['lock_hex_uuid'] = \
            '2543dc188d4611eba1fda951d4e5fdb5'
        mock_connection().get = mock.MagicMock(return_value=(bytes_uuid, None))
        mock_connection().delete = mock.MagicMock(return_value=True)

        # act
        lock.delete(etcd_resource=None)

        # assert
        mock_connection().delete.assert_called_with('/locks/test_lock')

    def test_refresh(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='LockTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.refresh')

        # assert
        self.assertTrue(False)

    def test_acquirement_valid(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='LockTestCase',
            ctx_operation_name='cloudify.interfaces.validation.acquirement')
        bytes_uuid = '%C\xdc\x18\x8dF\x11\xeb\xa1\xfd\xa9Q\xd4\xe5\xfd\xb5'
        self._ctx.instance.runtime_properties['lock_key'] = '/locks/test_lock'
        self._ctx.instance.runtime_properties['lock_hex_uuid'] = \
            '2543dc188d4611eba1fda951d4e5fdb5'
        mock_connection().get = mock.MagicMock(return_value=(bytes_uuid, None))

        # act
        lock.acquirement_validation(etcd_resource=None)

    def test_acquirement_invalid(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='LockTestCase',
            ctx_operation_name='cloudify.interfaces.validation.acquirement')
        uuid_bytes = None
        self._ctx.instance.runtime_properties['lock_key'] = '/locks/test_lock'
        self._ctx.instance.runtime_properties['lock_hex_uuid'] = \
            '2543dc188d4611eba1fda951d4e5fdb5'
        mock_connection().get = mock.MagicMock(return_value=(uuid_bytes, None))

        # act
        with self.assertRaises(NonRecoverableError):
            lock.acquirement_validation(etcd_resource=None)
