# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/base64_utils.py
import logging
import base64
import binascii
import cPickle
import typing
_logger = logging.getLogger(__name__)

def base64UrlDecode(encodedValue):
    if isinstance(encodedValue, unicode):
        encodedValue = encodedValue.encode('ascii')
    rem = len(encodedValue) % 4
    if rem > 0:
        encodedValue += '=' * (4 - rem)
    return base64.urlsafe_b64decode(encodedValue)


def pack(raw):
    try:
        return base64.b64encode(cPickle.dumps(raw, cPickle.HIGHEST_PROTOCOL))
    except (binascii.Error,
     cPickle.PickleError,
     UnicodeError,
     TypeError,
     ValueError):
        _logger.exception('Packing data fail.')

    return None


def unpack(packed, default=None):
    try:
        return cPickle.loads(base64.b64decode(packed))
    except (binascii.Error,
     cPickle.PickleError,
     UnicodeError,
     TypeError,
     ValueError):
        _logger.exception('Unpacking data fail.')

    return default
