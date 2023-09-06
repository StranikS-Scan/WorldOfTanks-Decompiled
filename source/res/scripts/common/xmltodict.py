# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/xmltodict.py
try:
    from defusedexpat import pyexpat as expat
except ImportError:
    from xml.parsers import expat

from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

OrderedDict = dict
try:
    _basestring = basestring
except NameError:
    _basestring = str

try:
    _unicode = unicode
except NameError:
    _unicode = str

__author__ = 'Martin Blech'
__version__ = '0.11.0'
__license__ = 'MIT'

class ParsingInterrupted(Exception):
    pass


class _DictSAXHandler(object):

    def __init__(self, item_depth=0, item_callback=lambda *args: True, xml_attribs=True, attr_prefix='@', cdata_key='#text', force_cdata=False, cdata_separator='', postprocessor=None, dict_constructor=OrderedDict, strip_whitespace=True, namespace_separator=':', namespaces=None, force_list=None):
        self.path = []
        self.stack = []
        self.data = []
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.dict_constructor = dict_constructor
        self.strip_whitespace = strip_whitespace
        self.namespace_separator = namespace_separator
        self.namespaces = namespaces
        self.namespace_declarations = OrderedDict()
        self.force_list = force_list
        return

    def _build_name(self, full_name):
        if not self.namespaces:
            return full_name
        i = full_name.rfind(self.namespace_separator)
        if i == -1:
            return full_name
        namespace, name = full_name[:i], full_name[i + 1:]
        short_namespace = self.namespaces.get(namespace, namespace)
        return name if not short_namespace else self.namespace_separator.join((short_namespace, name))

    def _attrs_to_dict(self, attrs):
        return attrs if isinstance(attrs, dict) else self.dict_constructor(zip(attrs[0::2], attrs[1::2]))

    def startNamespaceDecl(self, prefix, uri):
        self.namespace_declarations[prefix or ''] = uri

    def startElement(self, full_name, attrs):
        name = self._build_name(full_name)
        attrs = self._attrs_to_dict(attrs)
        if attrs and self.namespace_declarations:
            attrs['xmlns'] = self.namespace_declarations
            self.namespace_declarations = OrderedDict()
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attr_entries = []
                for key, value in attrs.items():
                    key = self.attr_prefix + self._build_name(key)
                    if self.postprocessor:
                        entry = self.postprocessor(self.path, key, value)
                    else:
                        entry = (key, value)
                    if entry:
                        attr_entries.append(entry)

                attrs = self.dict_constructor(attr_entries)
            else:
                attrs = None
            self.item = attrs or None
            self.data = []
        return

    def endElement(self, full_name):
        name = self._build_name(full_name)
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = None if not self.data else self.cdata_separator.join(self.data)
            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if self.stack:
            data = None if not self.data else self.cdata_separator.join(self.data)
            item = self.item
            self.item, self.data = self.stack.pop()
            if self.strip_whitespace and data:
                data = data.strip() or None
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if item is not None:
                if data:
                    self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = None
            self.data = []
        self.path.pop()
        return

    def characters(self, data):
        if not self.data:
            self.data = [data]
        else:
            self.data.append(data)

    def push_data(self, item, key, data):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        if item is None:
            item = self.dict_constructor()
        try:
            value = item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                item[key] = [value, data]
        except KeyError:
            if self._should_force_list(key, data):
                item[key] = [data]
            else:
                item[key] = data

        return item

    def _should_force_list(self, key, value):
        if not self.force_list:
            return False
        try:
            return key in self.force_list
        except TypeError:
            return self.force_list(self.path[:-1], key, value)


def parse(xml_input, encoding=None, expat=expat, process_namespaces=False, namespace_separator=':', disable_entities=True, **kwargs):
    handler = _DictSAXHandler(namespace_separator=namespace_separator, **kwargs)
    if isinstance(xml_input, _unicode):
        if not encoding:
            encoding = 'utf-8'
        xml_input = xml_input.encode(encoding)
    if not process_namespaces:
        namespace_separator = None
    parser = expat.ParserCreate(encoding, namespace_separator)
    try:
        parser.ordered_attributes = True
    except AttributeError:
        pass

    parser.StartNamespaceDeclHandler = handler.startNamespaceDecl
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    parser.buffer_text = True
    if disable_entities:
        try:
            feature = 'http://apache.org/xml/features/disallow-doctype-decl'
            parser._reader.setFeature(feature, True)
        except AttributeError:
            parser.DefaultHandler = lambda x: None
            parser.ExternalEntityRefHandler = lambda *x: 1

    if hasattr(xml_input, 'read'):
        parser.ParseFile(xml_input)
    else:
        parser.Parse(xml_input, True)
    return handler.item


def _process_namespace(name, namespaces, ns_sep=':', attr_prefix='@'):
    if not namespaces:
        return name
    try:
        ns, name = name.rsplit(ns_sep, 1)
    except ValueError:
        pass
    else:
        ns_res = namespaces.get(ns.strip(attr_prefix))
        name = '{0}{1}{2}{3}'.format(attr_prefix if ns.startswith(attr_prefix) else '', ns_res, ns_sep, name) if ns_res else name

    return name


def _emit(key, value, content_handler, attr_prefix='@', cdata_key='#text', depth=0, preprocessor=None, pretty=False, newl='\n', indent='\t', namespace_separator=':', namespaces=None, full_document=True):
    key = _process_namespace(key, namespaces, namespace_separator, attr_prefix)
    if preprocessor is not None:
        result = preprocessor(key, value)
        if result is None:
            return
        key, value = result
    if not hasattr(value, '__iter__') or isinstance(value, (_basestring, dict)):
        value = [value]
    for index, v in enumerate(value):
        if full_document and depth == 0 and index > 0:
            raise ValueError('document with multiple roots')
        if v is None:
            v = OrderedDict()
        elif not isinstance(v, dict):
            v = _unicode(v)
        if isinstance(v, _basestring):
            v = OrderedDict(((cdata_key, v),))
        cdata = None
        attrs = OrderedDict()
        children = []
        for ik, iv in v.items():
            if ik == cdata_key:
                cdata = iv
                continue
            if ik.startswith(attr_prefix):
                ik = _process_namespace(ik, namespaces, namespace_separator, attr_prefix)
                if ik == '@xmlns' and isinstance(iv, dict):
                    for k, v in iv.items():
                        attr = 'xmlns{0}'.format(':{0}'.format(k) if k else '')
                        attrs[attr] = _unicode(v)

                    continue
                if not isinstance(iv, _unicode):
                    iv = _unicode(iv)
                attrs[ik[len(attr_prefix):]] = iv
                continue
            children.append((ik, iv))

        if pretty:
            content_handler.ignorableWhitespace(depth * indent)
        content_handler.startElement(key, AttributesImpl(attrs))
        if pretty and children:
            content_handler.ignorableWhitespace(newl)
        for child_key, child_value in children:
            _emit(child_key, child_value, content_handler, attr_prefix, cdata_key, depth + 1, preprocessor, pretty, newl, indent, namespaces=namespaces, namespace_separator=namespace_separator)

        if cdata is not None:
            content_handler.characters(cdata)
        if pretty and children:
            content_handler.ignorableWhitespace(depth * indent)
        content_handler.endElement(key)
        if pretty and depth:
            content_handler.ignorableWhitespace(newl)

    return


def unparse(input_dict, output=None, encoding='utf-8', full_document=True, short_empty_elements=False, xml_generator_cls=None, **kwargs):
    if full_document and len(input_dict) != 1:
        raise ValueError('Document must have exactly one root.')
    must_return = False
    if output is None:
        output = StringIO()
        must_return = True
    generator_cls = xml_generator_cls or XMLGenerator
    if short_empty_elements:
        content_handler = generator_cls(output, encoding, True)
    else:
        content_handler = generator_cls(output, encoding)
    if full_document:
        content_handler.startDocument()
    for key, value in input_dict.items():
        _emit(key, value, content_handler, full_document=full_document, **kwargs)

    if full_document:
        content_handler.endDocument()
    if must_return:
        value = output.getvalue()
        try:
            value = value.decode(encoding)
        except AttributeError:
            pass

        return value
    else:
        return


if __name__ == '__main__':
    import sys
    import marshal
    try:
        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer
    except AttributeError:
        stdin = sys.stdin
        stdout = sys.stdout

    item_depth_arg = int(sys.argv[1])

    def handle_item(path, item):
        marshal.dump((path, item), stdout)
        return True


    try:
        root = parse(stdin, item_depth=item_depth_arg, item_callback=handle_item, dict_constructor=dict)
        if item_depth_arg == 0:
            handle_item([], root)
    except KeyboardInterrupt:
        pass
