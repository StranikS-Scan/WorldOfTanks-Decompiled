# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-riscos/rourl2path.py
import string
import urllib
__all__ = ['url2pathname', 'pathname2url']
__slash_dot = string.maketrans('/.', './')

def url2pathname(url):
    tp = urllib.splittype(url)[0]
    if tp and tp != 'file':
        raise RuntimeError, 'Cannot convert non-local URL to pathname'
    if url[:3] == '///':
        url = url[2:]
    elif url[:2] == '//':
        raise RuntimeError, 'Cannot convert non-local URL to pathname'
    components = string.split(url, '/')
    if not components[0]:
        if '$' in components:
            del components[0]
        else:
            components[0] = '$'
    i = 0
    while i < len(components):
        if components[i] == '.':
            del components[i]
        if components[i] == '..' and i > 0 and components[i - 1] not in ('', '..'):
            del components[i - 1:i + 1]
            i -= 1
        if components[i] == '..':
            components[i] = '^'
            i += 1
        if components[i] == '' and i > 0 and components[i - 1] != '':
            del components[i]
        i += 1

    components = map(lambda x: urllib.unquote(x).translate(__slash_dot), components)
    return '.'.join(components)


def pathname2url(pathname):
    return urllib.quote('///' + pathname.translate(__slash_dot), '/$:')


def test():
    for url in ['index.html',
     '/SCSI::SCSI4/$/Anwendung/Comm/Apps/!Fresco/Welcome',
     '/SCSI::SCSI4/$/Anwendung/Comm/Apps/../!Fresco/Welcome',
     '../index.html',
     'bar/index.html',
     '/foo/bar/index.html',
     '/foo/bar/',
     '/']:
        print '%r -> %r' % (url, url2pathname(url))

    print '*******************************************************'
    for path in ['SCSI::SCSI4.$.Anwendung', 'PythonApp:Lib', 'PythonApp:Lib.rourl2path/py']:
        print '%r -> %r' % (path, pathname2url(path))


if __name__ == '__main__':
    test()
