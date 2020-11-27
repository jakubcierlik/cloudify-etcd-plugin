# Standard imports
import uuid

# Py2/3 compatibility
from etcd_sdk._compat import text_type


class QuotaException(Exception):
    pass


class InvalidDomainException(Exception):
    pass


class InvalidINSecureValue(Exception):
    pass


class EtcdResource(object):
    pass
