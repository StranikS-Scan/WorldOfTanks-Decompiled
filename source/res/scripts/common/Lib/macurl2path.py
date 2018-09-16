# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/macurl2path.py
import urllib
import os
__all__ = ['url2pathname', 'pathname2url']

def url2pathname(pathname):
    tp = urllib.splittype(pathname)[0]
    if tp and tp != 'file':
        raise RuntimeError, 'Cannot convert non-local URL to pathname'
    if pathname[:3] == '///':
        pathname = pathname[2:]
    elif pathname[:2] == '//':
        raise RuntimeError, 'Cannot convert non-local URL to pathname'
    components = pathname.split('/')
    i = 0
    while i < len(components):
        if components[i] == '.':
            del components[i]
        if components[i] == '..' and i > 0 and components[i - 1] not in ('', '..'):
            del components[i - 1:i + 1]
            i = i - 1
        if components[i] == '' and i > 0 and components[i - 1] != '':
            del components[i]
        i = i + 1

    if not components[0]:
        rv = ':'.join(components[1:])
    else:
        i = 0
        while i < len(components) and components[i] == '..':
            components[i] = ''
            i = i + 1

        rv = ':' + ':'.join(components)
    return urllib.unquote(rv)


def pathname2url(pathname):
    if '/' in pathname:
        raise RuntimeError, 'Cannot convert pathname containing slashes'
    components = pathname.split(':')
    if components[0] == '':
        del components[0]
    if components[-1] == '':
        del components[-1]
    for i in range(len(components)):
        if components[i] == '':
            components[i] = '..'

    components = map(_pncomp2url, components)
    if os.path.isabs(pathname):
        return '/' + '/'.join(components)
    else:
        return '/'.join(components)


def _pncomp2url(component):
    component = urllib.quote(component[:31], safe='')
    return component
