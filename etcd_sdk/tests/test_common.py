# Standard imports
import unittest

# Third party imports
import etcd3

# Local imports
from etcd_sdk.common import EtcdResource


class EtcdCommonBase(unittest.TestCase):

    def setUp(self):
        super(EtcdCommonBase, self).setUp()

    def test_etcd_resource_instance(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'},
            resource_config={'name': 'foo-name',
                             'id': '53eb39c5-ca18-4934-b82a-84a4df0dbaf5'}
        )
        self.assertEqual(resource.resource_id,
                         '53eb39c5-ca18-4934-b82a-84a4df0dbaf5')
        self.assertEqual(resource.name, 'foo-name')

    def test_valid_resource_id(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'},
            resource_config={'name': 'foo-name'}
        )
        self.assertIsNotNone(resource.resource_id)

    def test_valid_client_config(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'}
        )
        self.assertEqual(resource.client_config, {'host': 'localhost'})

    def test_valid_connection(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'},
            resource_config={'name': 'foo-name'}
        )
        self.assertIsInstance(resource.connection, etcd3.Etcd3Client)

    def test_empty_resource_name(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'}
        )
        self.assertIsNone(resource.name)

    def test_create(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'},
            resource_config={'name': 'foo-name',
                             'id': '53eb39c5-ca18-4934-b82a-84a4df0dbaf5'}
        )
        with self.assertRaises(NotImplementedError):
            resource.create()

    def test_get(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'},
            resource_config={'name': 'foo-name',
                             'id': '53eb39c5-ca18-4934-b82a-84a4df0dbaf5'}
        )
        with self.assertRaises(NotImplementedError):
            resource.get()

    def test_list(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'},
            resource_config={'name': 'foo-name',
                             'id': '53eb39c5-ca18-4934-b82a-84a4df0dbaf5'}
        )
        with self.assertRaises(NotImplementedError):
            resource.list()

    def test_delete(self):
        resource = EtcdResource(
            client_config={'host': 'localhost'},
            resource_config={'name': 'foo-name',
                             'id': '53eb39c5-ca18-4934-b82a-84a4df0dbaf5'}
        )
        with self.assertRaises(NotImplementedError):
            resource.delete()
