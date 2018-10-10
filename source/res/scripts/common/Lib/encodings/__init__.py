# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/encodings/__init__.py
import codecs
from encodings import aliases
import __builtin__
_cache = {}
_unknown = '--unknown--'
_import_tail = ['*']
_norm_encoding_map = '                                              . 0123456789       ABCDEFGHIJKLMNOPQRSTUVWXYZ      abcdefghijklmnopqrstuvwxyz                                                                                                                                     '
_aliases = aliases.aliases

class CodecRegistryError(LookupError, SystemError):
    pass


def normalize_encoding(encoding):
    if hasattr(__builtin__, 'unicode') and isinstance(encoding, unicode):
        encoding = encoding.encode('latin-1')
    return '_'.join(encoding.translate(_norm_encoding_map).split())


def search_function(encoding):
    entry = _cache.get(encoding, _unknown)
    if entry is not _unknown:
        return entry
    else:
        norm_encoding = normalize_encoding(encoding)
        aliased_encoding = _aliases.get(norm_encoding) or _aliases.get(norm_encoding.replace('.', '_'))
        if aliased_encoding is not None:
            modnames = [aliased_encoding, norm_encoding]
        else:
            modnames = [norm_encoding]
        for modname in modnames:
            if not modname or '.' in modname:
                continue
            try:
                mod = __import__('encodings.' + modname, fromlist=_import_tail, level=0)
            except ImportError:
                pass
            else:
                break

        else:
            mod = None

        try:
            getregentry = mod.getregentry
        except AttributeError:
            mod = None

        if mod is None:
            _cache[encoding] = None
            return
        entry = getregentry()
        if not isinstance(entry, codecs.CodecInfo):
            if not 4 <= len(entry) <= 7:
                raise CodecRegistryError, 'module "%s" (%s) failed to register' % (mod.__name__, mod.__file__)
            if not hasattr(entry[0], '__call__') or not hasattr(entry[1], '__call__') or entry[2] is not None and not hasattr(entry[2], '__call__') or entry[3] is not None and not hasattr(entry[3], '__call__') or len(entry) > 4 and entry[4] is not None and not hasattr(entry[4], '__call__') or len(entry) > 5 and entry[5] is not None and not hasattr(entry[5], '__call__'):
                raise CodecRegistryError, 'incompatible codecs in module "%s" (%s)' % (mod.__name__, mod.__file__)
            if len(entry) < 7 or entry[6] is None:
                entry += (None,) * (6 - len(entry)) + (mod.__name__.split('.', 1)[1],)
            entry = codecs.CodecInfo(*entry)
        _cache[encoding] = entry
        try:
            codecaliases = mod.getaliases()
        except AttributeError:
            pass
        else:
            for alias in codecaliases:
                if alias not in _aliases:
                    _aliases[alias] = modname

        return entry


codecs.register(search_function)
