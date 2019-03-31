# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/i18n.py
# Compiled at: 2012-01-23 14:10:35
from encodings import utf_8
import gettext, constants
import BigWorld
import json
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
g_translators = {}

def convert(utf8String):
    try:
        return utf_8.decode(utf8String)[0]
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_WARNING('Wrong UTF8 string', utf8String)
        return utf_8.decode('----')[0]


def makeString(key, *args, **kargs):
    global g_translators
    try:
        if not key or key[0] != '#':
            return key
        moName, subkey = key[1:].split(':', 1)
        if not moName or not subkey:
            return key
        translator = g_translators.get(moName)
        if translator is None:
            path = convert(BigWorld.wg_resolveFileName('text')[:-5])
            translator = gettext.translation(moName, path, languages=['text'])
            g_translators[moName] = translator
        text = translator.gettext(subkey)
        if text == '?empty?':
            text = ''
        if args:
            try:
                text = text % args
            except TypeError:
                LOG_WARNING("Arguments do not match string read by key '%s': %s", (key, args))
                return key

        elif kargs:
            try:
                text = text % kargs
            except TypeError:
                LOG_WARNING("Arguments do not match string read by key '%s': %s", (key, kargs))
                return key

        return text
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_WARNING('Key string incompatible with args', key, args, kargs)
        return key

    return


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
            else:
                utf8args.append(v)

        return makeString(key, *tuple(utf8args))
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_WARNING('Failed to translate JSON-encoded string to dict or list', key, argsStr)
        return key
