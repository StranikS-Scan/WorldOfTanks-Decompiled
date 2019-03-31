# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/xml/etree/ElementInclude.py
# Compiled at: 2010-05-25 20:46:16
import copy
import ElementTree
XINCLUDE = '{http://www.w3.org/2001/XInclude}'
XINCLUDE_INCLUDE = XINCLUDE + 'include'
XINCLUDE_FALLBACK = XINCLUDE + 'fallback'

class FatalIncludeError(SyntaxError):
    pass


def default_loader(href, parse, encoding=None):
    file = open(href)
    if parse == 'xml':
        data = ElementTree.parse(file).getroot()
    else:
        data = file.read()
        if encoding:
            data = data.decode(encoding)
    file.close()
    return data


def include(elem, loader=None):
    if loader is None:
        loader = default_loader
    i = 0
    while 1:
        if i < len(elem):
            e = elem[i]
            if e.tag == XINCLUDE_INCLUDE:
                href = e.get('href')
                parse = e.get('parse', 'xml')
                node = parse == 'xml' and loader(href, parse)
                raise node is None and FatalIncludeError('cannot load %r as %r' % (href, parse))
            node = copy.copy(node)
            if e.tail:
                if not node.tail:
                    node.tail = '' + e.tail
                elem[i] = node
            elif parse == 'text':
                text = loader(href, parse, e.get('encoding'))
                if text is None:
                    raise FatalIncludeError('cannot load %r as %r' % (href, parse))
                if i:
                    node = elem[i - 1]
                    node.tail = node.tail or '' + text
                else:
                    elem.text = elem.text or '' + text + (e.tail or '')
                del elem[i]
                continue
            else:
                raise FatalIncludeError('unknown parse type in xi:include tag (%r)' % parse)
        elif e.tag == XINCLUDE_FALLBACK:
            raise FatalIncludeError('xi:fallback tag must be child of xi:include (%r)' % e.tag)
        else:
            include(e, loader)
        i = i + 1

    return
