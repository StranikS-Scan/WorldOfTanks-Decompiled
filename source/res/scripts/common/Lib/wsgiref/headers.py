# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/wsgiref/headers.py
from types import ListType, TupleType
import re
tspecials = re.compile('[ \\(\\)<>@,;:\\\\"/\\[\\]\\?=]')

def _formatparam(param, value=None, quote=1):
    if value is not None and len(value) > 0:
        if quote or tspecials.search(value):
            value = value.replace('\\', '\\\\').replace('"', '\\"')
            return '%s="%s"' % (param, value)
        else:
            return '%s=%s' % (param, value)
    else:
        return param
    return


class Headers:

    def __init__(self, headers):
        if type(headers) is not ListType:
            raise TypeError('Headers must be a list of name/value tuples')
        self._headers = headers

    def __len__(self):
        return len(self._headers)

    def __setitem__(self, name, val):
        del self[name]
        self._headers.append((name, val))

    def __delitem__(self, name):
        name = name.lower()
        self._headers[:] = [ kv for kv in self._headers if kv[0].lower() != name ]

    def __getitem__(self, name):
        return self.get(name)

    def has_key(self, name):
        return self.get(name) is not None

    __contains__ = has_key

    def get_all(self, name):
        name = name.lower()
        return [ kv[1] for kv in self._headers if kv[0].lower() == name ]

    def get(self, name, default=None):
        name = name.lower()
        for k, v in self._headers:
            if k.lower() == name:
                return v

        return default

    def keys(self):
        return [ k for k, v in self._headers ]

    def values(self):
        return [ v for k, v in self._headers ]

    def items(self):
        return self._headers[:]

    def __repr__(self):
        return 'Headers(%r)' % self._headers

    def __str__(self):
        return '\r\n'.join([ '%s: %s' % kv for kv in self._headers ] + ['', ''])

    def setdefault(self, name, value):
        result = self.get(name)
        if result is None:
            self._headers.append((name, value))
            return value
        else:
            return result
            return

    def add_header(self, _name, _value, **_params):
        parts = []
        if _value is not None:
            parts.append(_value)
        for k, v in _params.items():
            if v is None:
                parts.append(k.replace('_', '-'))
            parts.append(_formatparam(k.replace('_', '-'), v))

        self._headers.append((_name, '; '.join(parts)))
        return
