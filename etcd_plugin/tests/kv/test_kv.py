# Third party imports
from collections import namedtuple
import mock

# Local imports
from etcd_plugin.tests.base import EtcdTestBase
from etcd_plugin.resources import keyvaluepair
from cloudify.exceptions import RecoverableError, NonRecoverableError


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
        self.assertEqual(self._ctx.instance.runtime_properties['key'],
                         'test_key')

        self.assertEqual(self._ctx.instance.runtime_properties['value'],
                         'test_value')

    def test_create_protect_overwrite(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'previous_value'

        mock_connection().get = mock.MagicMock(return_value=(value, metadata))
        mock_connection().put = mock.MagicMock()

        # act
        with self.assertRaises(RecoverableError):
            keyvaluepair.create(etcd_resource=None,
                                fail_on_overwrite=True)

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
            test_name='ExternalKeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create',
            test_properties=properties,
            test_runtime_properties={
                'key': b'test_ext_key',
                'value': b'test_ext_value',
            })
        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'test_ext_value'
        mock_connection().get = mock.MagicMock(return_value=(value, metadata))

        # act
        keyvaluepair.create(etcd_resource=None)

        # assert
        self.assertEqual(self._ctx.instance.runtime_properties['key'],
                         'test_ext_key')

        self.assertEqual(self._ctx.instance.runtime_properties['value'],
                         'test_ext_value')

    def test_create_from_args(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create')
        mock_connection().put = mock.MagicMock()

        # act
        keyvaluepair.create(etcd_resource=None,
                            key=b'test_arg_key',
                            value=b'test_arg_value')

        # assert
        self.assertEqual(self._ctx.instance.runtime_properties['key'],
                         'test_arg_key')

        self.assertEqual(self._ctx.instance.runtime_properties['value'],
                         'test_arg_value')

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

    def test_delete_fail_on_overwrite(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')

        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'test_value'

        Container = namedtuple('Container', 'key create_revision mod_revision'
                                            ' version value')
        container = Container('test_key', 14, 15, 1, 'test_value')
        DeleteRangeResponse = namedtuple('DeleteRangeResponse',
                                         'deleted prev_kvs')
        delete_range_response = DeleteRangeResponse(1L, [container])
        mock_connection().get = mock.MagicMock(return_value=(value, metadata))
        mock_connection().delete = mock.MagicMock(
            return_value=delete_range_response)

        self._ctx.node.properties['resource_config']['fail_on_overwrite'] \
            = True

        # act
        keyvaluepair.delete(etcd_resource=None)

        # assert
        mock_connection().delete.assert_called_with('test_key',
                                                    prev_kv=True,
                                                    return_response=True)

    def test_delete_fail_on_race(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='KeyValuePairTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')

        Metadata = namedtuple('Metadata', 'version')
        metadata = Metadata(1L)
        value = b'test_value'

        Container = namedtuple('Container', 'key create_revision mod_revision'
                                            ' version value')
        container = Container('test_key', 14, 15, 1, 'bar1')
        DeleteRangeResponse = namedtuple('DeleteRangeResponse',
                                         'deleted prev_kvs')
        delete_range_response = DeleteRangeResponse(1L, [container])
        mock_connection().get = mock.MagicMock(return_value=(value, metadata))
        mock_connection().delete = mock.MagicMock(
            return_value=delete_range_response)

        self._ctx.node.properties['resource_config']['fail_on_overwrite'] \
            = True

        # act
        with self.assertRaises(NonRecoverableError):
            keyvaluepair.delete(etcd_resource=None)

        # assert
        mock_connection().delete.assert_called_with('test_key',
                                                    prev_kv=True,
                                                    return_response=True)
