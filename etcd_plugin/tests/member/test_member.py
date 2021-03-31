# Third party imports
from collections import namedtuple
import mock

# Local imports
from etcd_plugin.tests.base import EtcdTestBase
from etcd_plugin import member


@mock.patch('etcd3.client')
class MemberTestCase(EtcdTestBase):

    def setUp(self):
        super(MemberTestCase, self).setUp()

    @property
    def resource_config(self):
        return {
            'name': b'test_member',
            'peer_urls': ['http://127.0.0.1:2380'],
        }

    def test_create(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='MemberTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.create')
        Member = namedtuple('Member', 'id peer_urls')
        member_obj = Member(10501334649042878790, ['http://127.0.0.1:2380'])
        mock_connection().add_member = mock.MagicMock(return_value=member_obj)

        # act
        member.create(etcd_resource=None)

        # assert
        self.assertEqual(self._ctx.instance.runtime_properties['peer_urls'],
                         ['http://127.0.0.1:2380'])

    def test_delete(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='MemberTestCase',
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        self._ctx.instance.runtime_properties['member_id'] = \
            18129864113152051069
        mock_connection().remove_member = mock.MagicMock()

        # act
        member.delete(etcd_resource=None)

        # assert
        mock_connection().remove_member\
            .assert_called_with(18129864113152051069)

    def test_update(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='MemberTestCase',
            ctx_operation_name='cloudify.interfaces.operations.update')
        self._ctx.instance.runtime_properties['member_id'] = \
            18129864113152051069
        self._ctx.instance.runtime_properties['peer_urls'] = \
            ['http://127.0.0.1:2380']
        mock_connection().update_member = mock.MagicMock()

        # act
        member.update(etcd_resource=None)

        # assert
        mock_connection().update_member.assert_called_with(
            18129864113152051069,
            ['http://127.0.0.1:2380']
        )

    def test_disarm_member(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='MemberTestCase',
            ctx_operation_name='cloudify.interfaces.operations.disarm')
        self._ctx.instance.runtime_properties['member_id'] = \
            18129864113152051069
        Alarm = namedtuple('Alarm', 'alarm_type member_id')
        alarms = [Alarm(1, 18129864113152051070L)]
        mock_connection().disarm_alarm = mock.MagicMock(return_value=alarms)

        # act
        member.disarm(etcd_resource=None)

        # assert
        mock_connection().disarm_alarm\
            .assert_called_with(18129864113152051069)

    def test_disarm_all(self, mock_connection):
        # arrange
        self._prepare_context_for_operation(
            test_name='MemberTestCase',
            ctx_operation_name='cloudify.interfaces.operations.disarm')
        self._ctx.instance.runtime_properties['member_id'] = \
            18129864113152051069
        alarms = []
        mock_connection().disarm_alarm = mock.MagicMock(return_value=alarms)

        # act
        member.disarm(etcd_resource=None, member_id='all')

        # assert
        mock_connection().disarm_alarm.assert_called_with(member_id=0)
