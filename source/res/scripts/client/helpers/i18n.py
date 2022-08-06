# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/i18n.py
import json
import logging
import types
from encodings import utf_8
from frameworks import wulf
_logger = logging.getLogger(__name__)

def convert(utf8String):
    try:
        return utf_8.decode(utf8String)[0]
    except Exception as ex:
        _logger.exception(ex)
        _logger.warning('Wrong UTF8 string: %r', utf8String)
        return utf_8.decode('----')[0]


def isValidKey(key):
    return wulf.isTranslatedKeyValid(key)


def doesTextExist(key):
    return wulf.isTranslatedTextExisted(key)


def makeString(key, *args, **kwargs):
    if isinstance(key, bytes):
        key = unicode(key)
    if not key:
        return key
    if args:
        try:
            return wulf.getTranslatedText(key, args)
        except (TypeError, ValueError, KeyError):
            _logger.warning("Arguments do not match string read by key '%r': %r", key, args)
            return key

    elif kwargs:
        try:
            return wulf.getTranslatedText(key, kwargs)
        except (TypeError, ValueError, KeyError):
            _logger.warning("Arguments do not match string read by key '%s': %s", key, kwargs)
            return key

    return wulf.getTranslatedText(key)


def makePluralString(key, pluralKey, n, *args, **kwargs):
    if isinstance(key, bytes):
        key = unicode(key)
    if not key:
        return key
    if args:
        try:
            return wulf.getTranslatedPluralText(key, pluralKey, n, args)
        except (TypeError, ValueError, KeyError):
            _logger.warning("Arguments do not match string read by key '%r': %r", key, args)
            return key

    elif kwargs:
        try:
            return wulf.getTranslatedPluralText(key, pluralKey, n, kwargs)
        except (TypeError, ValueError, KeyError):
            _logger.warning("Arguments do not match string read by key '%s': %s", key, kwargs)
            return key

    return wulf.getTranslatedPluralText(key, pluralKey, n)


def makeStringJSON(key, argsStr):
    try:
        args = json.loads(argsStr)
        if isinstance(args, dict):
            utf8args = {}
            for k, v in args.iteritems():
                utf8args[k.encode('utf-8')] = v.encode('utf-8')

            return makeString(key, **utf8args)
        utf8args = []
        for v in args:
            if isinstance(v, str):
                utf8args.append(v.encode('utf-8'))
            utf8args.append(v)

        return makeString(key, *tuple(utf8args))
    except Exception as ex:
        _logger.exception(ex)
        _logger.warning('Failed to translate JSON-encoded string to dict or list: %r, %r', key, argsStr)
        return key


def encodeUtf8(string):
    return string.encode('utf-8', 'ignore') if isinstance(string, types.UnicodeType) else string
