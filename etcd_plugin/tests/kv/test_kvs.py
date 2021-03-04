# Third party imports
from collections import namedtuple
import mock

# Local imports
from etcd_plugin.tests.base import EtcdTestBase
from etcd_plugin import keyvaluepairs


@mock.patch('etcd3.client')
class KeyValuePairTestCase(EtcdTestBase):

    def setUp(self):
        super(KeyValuePairTestCase, self).setUp()

    @property
    def resource_config(self):
        return [
            {
                'kvpair': {
                    'key': 'test_key1',
                    'value': 'test_value1'
                }
            }, {
                'kvpair': {
                    'key': 'test_key2',
                    'value': 'test_value2'
                }
            }
        ]

    def test_create(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairsTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create')
        mock_connection().put = mock.MagicMock()

        # act
        keyvaluepairs.create(etcd_resource=None)

        # assert
        self.assertEqual(self._ctx.instance.runtime_properties['test_key1'],
                         'test_value1')

        self.assertEqual(self._ctx.instance.runtime_properties['test_key2'],
                         'test_value2')

    def test_create_external_resource(self, mock_connection):
        # arrange
        properties = dict()
        # Enable external resource
        properties['use_external_resource'] = True

        # Add node properties config to this dict
        properties.update(self.node_properties)
        # Reset resource config since we are going to use external resource
        # and do not care about the resource config data
        properties['resource_config'] = [
            {
                'kvpair': {
                    'key': 'test_key1',
                    'value': 'test_value1'
                }
            }, {
                'kvpair': {
                    'key': 'test_key2',
                    'value': 'test_value2'
                }
            }
        ]

        # Prepare the context for create operation
        self._prepare_context_for_operation(
            test_name='ExternalKeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create',
            test_properties=properties,
            test_runtime_properties={
                b'test_ext_key1': b'test_ext_value1',
                b'test_ext_key2': b'test_ext_value2',
            })
        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'test_ext_value'
        mock_connection().get = mock.MagicMock(return_value=(value, metadata))

        # act
        keyvaluepairs.create(etcd_resource=None)

        # assert
        self.assertEqual(
            self._ctx.instance.runtime_properties['test_ext_key1'],
            'test_ext_value1'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['test_ext_key2'],
            'test_ext_value2'
        )

    def test_delete(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_connection().delete = mock.MagicMock(return_value=True)

        # act
        keyvaluepairs.delete(etcd_resource=None)

        # assert
        # the assert below stores only the last call parameter
        mock_connection().delete.assert_called_with('test_key2',
                                                    prev_kv=mock.ANY,
                                                    return_response=mock.ANY)
        self.assertEqual(mock_connection().delete.call_count, 2)
