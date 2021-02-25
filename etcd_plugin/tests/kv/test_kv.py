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

    def test_create_external_resource(self, mock_connection):
        # arrange
        properties = dict()
        # Enable external resource
        properties['use_external_resource'] = True

        # Add node properties config to this dict
        properties.update(self.node_properties)
        # Reset resource config since we are going to use external resource
        # and do not care about the resource config data
        properties['resource_config'] = {
            'name': 'test_ext_keyvaluepair',
            'key': b'test_ext_key',
            'value': b'test_ext_value',
        }

        # Prepare the context for create operation
        self._prepare_context_for_operation(
            test_name='ExternaleyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create',
            test_properties=properties,
            test_runtime_properties={
                b'test_ext_key': b'test_ext_value',
            })

        # act
        keyvaluepair.create(etcd_resource=None)

        # assert
        self.assertEqual(self._ctx.instance.runtime_properties['test_ext_key'],
                         'test_ext_value')

    def test_delete(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_connection().delete = mock.MagicMock(return_value=True)

        # act
        keyvaluepair.delete(etcd_resource=None)

        # assert
        mock_connection().delete.assert_called_with('test_key',
                                                    prev_kv=mock.ANY,
                                                    return_response=mock.ANY)
