# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/nturl2path.py
# Compiled at: 2032-09-30 08:24:07
"""Convert a NT pathname to a file URL and vice versa."""

def url2pathname(url):
    """OS-specific conversion from a relative URL of the 'file' scheme
    to a file system path; not recommended for general use."""
    import string, urllib
    url = url.replace(':', '|')
    if '|' not in url:
        if url[:4] == '////':
            url = url[2:]
        components = url.split('/')
        return urllib.unquote('\\'.join(components))
    comp = url.split('|')
    if len(comp) != 2 or comp[0][-1] not in string.ascii_letters:
        error = 'Bad URL: ' + url
        raise IOError, error
    drive = comp[0][-1].upper()
    path = drive + ':'
    components = comp[1].split('/')
    for comp in components:
        if comp:
            path = path + '\\' + urllib.unquote(comp)

    if path.endswith(':') and url.endswith('/'):
        path += '\\'
    return path


def pathname2url(p):
    """OS-specific conversion from a file system path to a relative URL
    of the 'file' scheme; not recommended for general use."""
    import urllib
    if ':' not in p:
        if p[:2] == '\\\\':
            p = '\\\\' + p
        components = p.split('\\')
        return urllib.quote('/'.join(components))
    comp = p.split(':')
    if len(comp) != 2 or len(comp[0]) > 1:
        error = 'Bad path: ' + p
        raise IOError, error
    drive = urllib.quote(comp[0].upper())
    components = comp[1].split('\\')
    path = '///' + drive + ':'
    for comp in components:
        if comp:
            path = path + '/' + urllib.quote(comp)

    return path
