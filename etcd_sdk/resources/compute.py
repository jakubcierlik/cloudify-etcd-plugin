from etcd_sdk.common import EtcdResource


class OpenstackKeyValuePair(EtcdResource):
    pass

# class OpenstackServer(OpenstackResource):
#     service_type = 'compute'
#     resource_type = 'server'

#     def list(self, details=True, all_projects=False, query=None):
#         query = query or {}
#         all_projects = query.pop('all_projects', False) or all_projects
#         self.logger.debug('Attempting to list servers')
#         return self.connection.compute.servers(details, all_projects, **query)

#     def get(self):
#         server = self.find_server()
#         return server

#     def find_server(self, name_or_id=None):
#         if not name_or_id:
#             name_or_id = self.name if not\
#                 self.resource_id else self.resource_id
#         self.logger.debug(
#             'Attempting to find this server: {0}'.format(name_or_id))
#         server = self.connection.compute.find_server(
#             name_or_id, ignore_missing=False
#         )
#         self.logger.debug(
#             'Found server with this result: {0}'.format(server))
#         return server

#     def create(self):
#         self.logger.debug(
#             'Attempting to create server with these args: {0}'.format(
#                 self.config))
#         server = self.connection.compute.create_server(**self.config)
#         self.logger.info(
#             'Created server with this result: {0}'.format(server))
#         return server

#     def delete(self):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to delete this server: {0}'.format(server))
#         result = self.connection.compute.delete_server(server)
#         self.logger.debug(
#             'Deleted server with this result: {0}'.format(result))
#         return result

#     def reboot(self, reboot_type):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to reboot this server: {0}'.format(server))
#         self.connection.compute.reboot_server(server, reboot_type)
#         return None

#     def resume(self):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to resume this server: {0}'.format(server))
#         self.connection.compute.resume_server(server)
#         return None

#     def suspend(self):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to suspend this server: {0}'.format(server))
#         self.connection.compute.suspend_server(server)
#         return None

#     def backup(self, name, backup_type, rotation):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to backup this server: {0}'.format(server))
#         self.connection.compute.backup_server(server,
#                                               name,
#                                               backup_type,
#                                               rotation)
#         return None

#     def rebuild(self, image, name=None, admin_password='', **attr):
#         server = self.get()
#         name = name or server.name
#         attr['image'] = image
#         self.logger.debug(
#             'Attempting to rebuild this server: {0}'.format(server))

#         self.connection.compute.rebuild_server(server,
#                                                name,
#                                                admin_password,
#                                                **attr)
#         return None

#     def create_image(self, name, metadata=None):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to create image for this server: {0}'.format(server))
#         self.connection.compute.create_server_image(
#             server, name, metadata=metadata
#         )
#         return None

#     def update(self, new_config=None):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to update this server: {0} with args {1}'.format(
#                 server, new_config))
#         result = self.connection.compute.update_server(server, **new_config)
#         self.logger.debug(
#             'Updated server with this result: {0}'.format(result))
#         return result

#     def start(self):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to start this server: {0}'.format(server))
#         self.connection.compute.start_server(server)
#         return None

#     def stop(self):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to stop this server: {0}'.format(server))
#         self.connection.compute.stop_server(server)
#         return None

#     def get_server_password(self):
#         server = self.get()
#         self.logger.debug(
#             'Attempting to get server'
#             ' password for this server: {0}'.format(server))
#         return self.connection.compute.get_server_password(server)

#     def list_volume_attachments(self):
#         self.logger.debug('Attempting to list volumes attachments')
#         return self.connection.compute.volume_attachments(self.resource_id)

#     def get_volume_attachment(self, attachment_id):
#         self.logger.debug(
#             'Attempting to find this volume attachment: {0}'
#             ''.format(attachment_id))
#         volume_attachment = \
#             self.connection.compute.get_volume_attachment(
#                 attachment_id, self.resource_id)
#         self.logger.debug(
#             'Found volume attachment with this result: {0}'
#             ''.format(volume_attachment))
#         return volume_attachment

#     def create_volume_attachment(self, attachment_config):
#         self.logger.debug(
#             'Attempting to create volume attachment'
#             ' with these args: {0}'.format(self.config))
#         volume_attachment = \
#             self.connection.compute.create_volume_attachment(
#                 self.resource_id, **attachment_config)
#         self.logger.debug(
#             'Created volume attachment with this result: {0}'
#             ''.format(volume_attachment))
#         return volume_attachment

#     def delete_volume_attachment(self, attachment_id):
#         self.logger.debug(
#             'Attempting to delete this volume attachment: {0}'
#             ''.format(attachment_id))
#         self.connection.compute.delete_volume_attachment(attachment_id,
#                                                          self.resource_id)
#         self.logger.debug(
#             'Volume attachment {0} was deleted successfully'
#             ''.format(attachment_id))
#         return None

#     def create_server_interface(self, interface_config):
#         self.logger.debug(
#             'Attempting to create server interface with these args:'
#             '{0}'.format(interface_config))
#         result = \
#             self.connection.compute.create_server_interface(
#                 self.resource_id, **interface_config)
#         self.logger.debug(
#             'Created server interface with this result: {0}'.format(result))
#         return result

#     def delete_server_interface(self, interface_id):
#         self.logger.debug(
#             'Attempting to delete server interface with these args:'
#             '{0}'.format(interface_id))
#         self.connection.compute.delete_server_interface(
#             interface_id, server=self.resource_id)
#         self.logger.debug(
#             'Server interface {0} was deleted successfully'
#             ''.format(interface_id))
#         return None

#     def get_server_interface(self, interface_id):
#         self.logger.debug(
#             'Attempting to find this server interface: {0}'
#             ''.format(interface_id))
#         server_interface = \
#             self.connection.compute.get_server_interface(
#                 interface_id, self.resource_id)
#         self.logger.debug(
#             'Found server interface with this result: {0}'
#             ''.format(server_interface))
#         return server_interface

#     def server_interfaces(self):
#         self.logger.debug('Attempting to list server interfaces')
#         return self.connection.compute.server_interfaces(self.resource_id)

#     def add_security_group_to_server(self, security_group_id):
#         self.logger.debug(
#             'Attempting to add security group {0} to server {1}'
#             ''.format(security_group_id, self.resource_id))
#         self.connection.compute.add_security_group_to_server(
#             self.resource_id, security_group_id)
#         self.logger.debug(
#             'Security group {0} was added to server {1} '
#             'successfully'.format(security_group_id, self.resource_id))
#         return None

#     def remove_security_group_from_server(self, security_group_id):
#         self.logger.debug(
#             'Attempting to remove security group {0} from server {1}'
#             ''.format(security_group_id, self.resource_id))
#         self.connection.compute.remove_security_group_from_server(
#             self.resource_id, security_group_id)
#         self.logger.debug(
#             'Security group {0} was removed from server {1} '
#             'successfully'.format(security_group_id, self.resource_id))
#         return None

#     def add_floating_ip_to_server(self, floating_ip, fixed_ip=None):
#         self.logger.debug(
#             'Attempting to add floating ip {0} to server {1}'
#             ''.format(floating_ip, self.resource_id))
#         self.connection.compute.add_floating_ip_to_server(
#             self.resource_id, floating_ip, fixed_address=fixed_ip)
#         self.logger.debug(
#             'Floating ip {0} was added to server {1} successfully'
#             ''.format(floating_ip, self.resource_id))
#         return None

#     def remove_floating_ip_from_server(self, floating_ip):
#         self.logger.debug(
#             'Attempting to remove floating ip {0} from server {1}'
#             ''.format(floating_ip, self.resource_id))
#         self.connection.compute.remove_floating_ip_from_server(
#             self.resource_id, floating_ip)
#         self.logger.debug(
#             'Floating ip {0} was removed from server {1} '
#             'successfully'.format(floating_ip, self.resource_id))
#         return None
