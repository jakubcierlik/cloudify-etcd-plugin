# # Standard imports
# import mock

# # Third party imports
# import etcd3

# # Local imports
# # from openstack_sdk.tests import base
# from etcd_sdk.resources import EtcdKeyValuePair


# class FlavorTestCase(base.OpenStackSDKTestBase):
#     def setUp(self):
#         super(FlavorTestCase, self).setUp()
#         self.fake_client = self.generate_fake_openstack_connection('flavor')
#         self.flavor_instance = compute.OpenstackFlavor(
#             client_config=self.client_config,
#             logger=mock.MagicMock()
#         )
#         self.flavor_instance.connection = self.connection

#     def test_get_flavor(self):
#         flavor = openstack.compute.v2.flavor.Flavor(**{
#             'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
#             'name': 'test_flavor',
#             'links': '2',
#             'os-flavor-access:is_public': True,
#             'ram': 6,
#             'vcpus': 8,
#             'swap': 8

#         })
#         self.flavor_instance.resource_id = \
#             'a95b5509-c122-4c2f-823e-884bb559afe8'
#         self.fake_client.find_flavor = mock.MagicMock(return_value=flavor)

#         response = self.flavor_instance.get()
#         self.assertEqual(response.id, 'a95b5509-c122-4c2f-823e-884bb559afe8')
#         self.assertEqual(response.links, '2')
#         self.assertEqual(response.name, 'test_flavor')

#     def test_list_flavors(self):
#         flavors = [
#             openstack.compute.v2.flavor.FlavorDetail(**{
#                 'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
#                 'name': 'test_flavor_1',
#                 'links': '2',
#                 'os-flavor-access:is_public': True,
#                 'ram': 6,
#                 'vcpus': 8,
#                 'swap': 8
#             }),
#             openstack.compute.v2.flavor.FlavorDetail(**{
#                 'id': 'fg5b5509-c122-4c2f-823e-884bb559afes',
#                 'name': 'test_flavor_2',
#                 'links': '3',
#                 'os-flavor-access:is_public': True,
#                 'ram': 4,
#                 'vcpus': 3,
#                 'swap': 3
#             })
#         ]

#         self.fake_client.flavors = mock.MagicMock(return_value=flavors)

#         response = self.flavor_instance.list()
#         self.assertEqual(len(response), 2)

#     def test_create_flavor(self):
#         flavor = {
#             'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
#             'links': '2',
#             'name': 'test_flavor',
#             'os-flavor-access:is_public': True,
#             'ram': 6,
#             'vcpus': 8,
#             'swap': 8
#         }

#         new_res = openstack.compute.v2.flavor.Flavor(**flavor)
#         self.flavor_instance.config = flavor
#         self.fake_client.create_flavor = mock.MagicMock(return_value=new_res)

#         response = self.flavor_instance.create()
#         self.assertEqual(response.id, flavor['id'])
#         self.assertEqual(response.name, flavor['name'])

#     def test_delete_flavor(self):
#         flavor = openstack.compute.v2.flavor.Flavor(**{
#             'id': 'a95b5509-c122-4c2f-823e-884bb559afe8',
#             'name': 'test_flavor',
#             'links': '2',
#             'os-flavor-access:is_public': True,
#             'ram': 6,
#             'vcpus': 8,
#             'swap': 8

#         })

#         self.flavor_instance.resource_id = \
#             'a95b5509-c122-4c2f-823e-884bb559afe8'
#         self.fake_client.get_flavor = mock.MagicMock(return_value=flavor)
#         self.fake_client.delete_flavor = mock.MagicMock(return_value=None)

#         response = self.flavor_instance.delete()
#         self.assertIsNone(response)
