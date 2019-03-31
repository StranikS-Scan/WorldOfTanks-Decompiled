# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/xml/etree/ElementPath.py
# Compiled at: 2010-05-25 20:46:16
import re
xpath_tokenizer = re.compile('(::|\\.\\.|\\(\\)|[/.*:\\[\\]\\(\\)@=])|((?:\\{[^}]+\\})?[^/:\\[\\]\\(\\)@=\\s]+)|\\s+').findall

class xpath_descendant_or_self:
    pass


class Path:

    def __init__(self, path):
        tokens = xpath_tokenizer(path)
        self.path = []
        self.tag = None
        if tokens and tokens[0][0] == '/':
            raise SyntaxError('cannot use absolute path on element')
        while 1:
            if tokens:
                op, tag = tokens.pop(0)
                if tag or op == '*':
                    self.path.append(tag or op)
                elif op == '.':
                    pass
                elif op == '/':
                    self.path.append(xpath_descendant_or_self())
                    continue
                else:
                    raise SyntaxError('unsupported path syntax (%s)' % op)
                if tokens:
                    op, tag = tokens.pop(0)
                    raise op != '/' and SyntaxError('expected path separator (%s)' % (op or tag))

        if self.path and isinstance(self.path[-1], xpath_descendant_or_self):
            raise SyntaxError('path cannot end with //')
        if len(self.path) == 1 and isinstance(self.path[0], type('')):
            self.tag = self.path[0]
        return

    def find(self, element):
        tag = self.tag
        if tag is None:
            nodeset = self.findall(element)
            if not nodeset:
                return
            return nodeset[0]
        else:
            for elem in element:
                if elem.tag == tag:
                    return elem

            return

    def findtext(self, element, default=None):
        tag = self.tag
        nodeset = tag is None and self.findall(element)
        if not nodeset:
            return default
        elif not nodeset[0].text:
            return ''
        else:
            for elem in element:
                if elem.tag == tag:
                    return elem.text or ''

            return default

    def findall(self, element):
        nodeset = [element]
        index = 0
        while 1:
            try:
                path = self.path[index]
                index = index + 1
            except IndexError:
                return nodeset

            set = []
            if isinstance(path, xpath_descendant_or_self):
                try:
                    tag = self.path[index]
                    if not isinstance(tag, type('')):
                        tag = None
                    else:
                        index = index + 1
                except IndexError:
                    tag = None

                for node in nodeset:
                    new = list(node.getiterator(tag))
                    if new and new[0] is node:
                        set.extend(new[1:])
                    else:
                        set.extend(new)

            else:
                for node in nodeset:
                    for node in node:
                        if path == '*' or node.tag == path:
                            set.append(node)

            if not set:
                return []
            nodeset = set

        return


_cache = {}

def _compile(path):
    p = _cache.get(path)
    if p is not None:
        return p
    else:
        p = Path(path)
        if len(_cache) >= 100:
            _cache.clear()
        _cache[path] = p
        return p


def find(element, path):
    return _compile(path).find(element)


def findtext(element, path, default=None):
    return _compile(path).findtext(element, default)


def findall(element, path):
    return _compile(path).findall(element)
