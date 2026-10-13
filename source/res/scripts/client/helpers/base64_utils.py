# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/base64_utils.py
from __future__ import absolute_import
import logging
import binascii
import typing
from future.moves import pickle
from past.builtins import unicode
from py2to3.compat import base64compat
_logger = logging.getLogger(__name__)

def base64UrlDecode(encodedValue):
    if isinstance(encodedValue, unicode):
        encodedValue = encodedValue.encode('ascii')
    rem = len(encodedValue) % 4
    if rem > 0:
        encodedValue += '=' * (4 - rem)
    return base64compat.urlsafe_b64decode(encodedValue)


def pack(raw):
    try:
        return base64compat.b64encode(pickle.dumps(raw, pickle.HIGHEST_PROTOCOL))
    except (binascii.Error,
     pickle.PickleError,
     UnicodeError,
     TypeError,
     ValueError):
        _logger.exception('Packing data fail.')

    return None


def unpack(packed, default=None):
    try:
        return pickle.loads(base64compat.b64decode(packed))
    except (binascii.Error,
     pickle.PickleError,
     UnicodeError,
     TypeError,
     ValueError,
     EOFError):
        _logger.exception('Unpacking data fail.')

    return default
