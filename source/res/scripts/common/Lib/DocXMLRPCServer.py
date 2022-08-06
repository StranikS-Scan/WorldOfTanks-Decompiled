# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/DocXMLRPCServer.py
import pydoc
import inspect
import re
import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler, CGIXMLRPCRequestHandler, resolve_dotted_attribute

def _html_escape_quote(s):
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('"', '&quot;')
    s = s.replace("'", '&#x27;')
    return s


class ServerHTMLDoc(pydoc.HTMLDoc):

    def markup(self, text, escape=None, funcs={}, classes={}, methods={}):
        escape = escape or self.escape
        results = []
        here = 0
        pattern = re.compile('\\b((http|ftp)://\\S+[\\w/]|RFC[- ]?(\\d+)|PEP[- ]?(\\d+)|(self\\.)?((?:\\w|\\.)+))\\b')
        while 1:
            match = pattern.search(text, here)
            if not match:
                break
            start, end = match.span()
            results.append(escape(text[here:start]))
            all, scheme, rfc, pep, selfdot, name = match.groups()
            if scheme:
                url = escape(all).replace('"', '&quot;')
                results.append('<a href="%s">%s</a>' % (url, url))
            elif rfc:
                url = 'http://www.rfc-editor.org/rfc/rfc%d.txt' % int(rfc)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            elif pep:
                url = 'http://www.python.org/dev/peps/pep-%04d/' % int(pep)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            elif text[end:end + 1] == '(':
                results.append(self.namelink(name, methods, funcs, classes))
            elif selfdot:
                results.append('self.<strong>%s</strong>' % name)
            else:
                results.append(self.namelink(name, classes))
            here = end

        results.append(escape(text[here:]))
        return ''.join(results)

    def docroutine(self, object, name, mod=None, funcs={}, classes={}, methods={}, cl=None):
        anchor = (cl and cl.__name__ or '') + '-' + name
        note = ''
        title = '<a name="%s"><strong>%s</strong></a>' % (self.escape(anchor), self.escape(name))
        if inspect.ismethod(object):
            args, varargs, varkw, defaults = inspect.getargspec(object.im_func)
            argspec = inspect.formatargspec(args[1:], varargs, varkw, defaults, formatvalue=self.formatvalue)
        elif inspect.isfunction(object):
            args, varargs, varkw, defaults = inspect.getargspec(object)
            argspec = inspect.formatargspec(args, varargs, varkw, defaults, formatvalue=self.formatvalue)
        else:
            argspec = '(...)'
        if isinstance(object, tuple):
            argspec = object[0] or argspec
            docstring = object[1] or ''
        else:
            docstring = pydoc.getdoc(object)
        decl = title + argspec + (note and self.grey('<font face="helvetica, arial">%s</font>' % note))
        doc = self.markup(docstring, self.preformat, funcs, classes, methods)
        doc = doc and '<dd><tt>%s</tt></dd>' % doc
        return '<dl><dt>%s</dt>%s</dl>\n' % (decl, doc)

    def docserver(self, server_name, package_documentation, methods):
        fdict = {}
        for key, value in methods.items():
            fdict[key] = '#-' + key
            fdict[value] = fdict[key]

        server_name = self.escape(server_name)
        head = '<big><big><strong>%s</strong></big></big>' % server_name
        result = self.heading(head, '#ffffff', '#7799ee')
        doc = self.markup(package_documentation, self.preformat, fdict)
        doc = doc and '<tt>%s</tt>' % doc
        result = result + '<p>%s</p>\n' % doc
        contents = []
        method_items = sorted(methods.items())
        for key, value in method_items:
            contents.append(self.docroutine(value, key, funcs=fdict))

        result = result + self.bigsection('Methods', '#ffffff', '#eeaa77', pydoc.join(contents))
        return result


class XMLRPCDocGenerator:

    def __init__(self):
        self.server_name = 'XML-RPC Server Documentation'
        self.server_documentation = 'This server exports the following methods through the XML-RPC protocol.'
        self.server_title = 'XML-RPC Server Documentation'

    def set_server_title(self, server_title):
        self.server_title = server_title

    def set_server_name(self, server_name):
        self.server_name = server_name

    def set_server_documentation(self, server_documentation):
        self.server_documentation = server_documentation

    def generate_html_documentation(self):
        methods = {}
        for method_name in self.system_listMethods():
            if method_name in self.funcs:
                method = self.funcs[method_name]
            elif self.instance is not None:
                method_info = [None, None]
                if hasattr(self.instance, '_get_method_argstring'):
                    method_info[0] = self.instance._get_method_argstring(method_name)
                if hasattr(self.instance, '_methodHelp'):
                    method_info[1] = self.instance._methodHelp(method_name)
                method_info = tuple(method_info)
                if method_info != (None, None):
                    method = method_info
                elif not hasattr(self.instance, '_dispatch'):
                    try:
                        method = resolve_dotted_attribute(self.instance, method_name)
                    except AttributeError:
                        method = method_info

                else:
                    method = method_info
            methods[method_name] = method

        documenter = ServerHTMLDoc()
        documentation = documenter.docserver(self.server_name, self.server_documentation, methods)
        title = _html_escape_quote(self.server_title)
        return documenter.page(title, documentation)


class DocXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):

    def do_GET(self):
        if not self.is_rpc_path_valid():
            self.report_404()
            return
        response = self.server.generate_html_documentation()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


class DocXMLRPCServer(SimpleXMLRPCServer, XMLRPCDocGenerator):

    def __init__(self, addr, requestHandler=DocXMLRPCRequestHandler, logRequests=1, allow_none=False, encoding=None, bind_and_activate=True):
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests, allow_none, encoding, bind_and_activate)
        XMLRPCDocGenerator.__init__(self)


class DocCGIXMLRPCRequestHandler(CGIXMLRPCRequestHandler, XMLRPCDocGenerator):

    def handle_get(self):
        response = self.generate_html_documentation()
        print 'Content-Type: text/html'
        print 'Content-Length: %d' % len(response)
        print
        sys.stdout.write(response)

    def __init__(self):
        CGIXMLRPCRequestHandler.__init__(self)
        XMLRPCDocGenerator.__init__(self)
