"""Python 2 + 3 compatibility utils"""
# flake8: noqa

import sys

PY2 = sys.version_info[0] == 2


if PY2:
    text_type = unicode
else:
    text_type = str

__all__ = [
    'PY2', 'text_type',
]
