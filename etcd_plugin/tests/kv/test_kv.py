# Third party imports
import mock

# Local imports
from etcd_plugin.tests.base import EtcdTestBase
from etcd_plugin import keyvaluepair


@mock.patch('etcd3.client')
class KeyValuePairTestCase(EtcdTestBase):

    def setUp(self):
        super(KeyValuePairTestCase, self).setUp()

    @property
    def resource_config(self):
        return {
            'name': 'test_keyvaluepair',
            'key': b'test_key',
            'value': b'test_value',
        }

    def test_create(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create')
        mock_connection().put = mock.MagicMock()

        # act
        keyvaluepair.create(etcd_resource=None)

        # assert
        self.assertEqual(self._ctx.instance.runtime_properties['test_key'],
                         'test_value')

    def test_create_ephemeral(self):
        # arrange
        # kv = KeyValue()
        # mock put
        # lease = ...

        # act
        # kv.create('foo', 'bar', lease=lease)

        # assert
        pass

    def test_delete(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairTestCase',
            test_runtime_properties={'test_key': 'test_value'},
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_connection().delete = mock.MagicMock(return_value=True)

        # act
        keyvaluepair.delete(etcd_resource=None)

        # assert
        for attr in ['test_key',
                     'test_value']:
            self.assertNotIn(attr,
                             self._ctx.instance.runtime_properties)

    def test_delete_prefix(self):
        pass

    def test_get(self):
        pass

    def test_get_prefix(self):
        pass

    def test_transaction(self):
        pass
