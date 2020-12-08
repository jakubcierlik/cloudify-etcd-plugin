class KeyValue:  # TODO(marrowne) inherit sth?

    def __init__(self):
        pass
    #     TODO(marrowne) create/inject Etcd3Client

    def create(self, key, value, lease=None):
        ...
        return None

    def delete(self, key):
        ...
        return None

    def delete_prefix(self, prefix):
        ...
        return None

    def get(self, key):  # TODO(marrowne) or read?
        ...
        return val

    def get_prefix(self, key_prefix, sort_order=None, sort_target='key', **kwargs):
        ...
        return val

    def transaction(self, compare, success=None, failure=None):
        ...
        return None
