# Embedded file name: scripts/client/helpers/html/templates.py
import ResMgr
from collections import defaultdict
from types import DictType
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_CURRENT_EXCEPTION
from helpers import html

class Template(object):

    def __init__(self, source, ctx = None):
        super(Template, self).__init__()
        self.source = source
        self.ctx = ctx

    def __repr__(self):
        return 'Template(source = {0:>s})'.format(self.source)

    def format(self, ctx = None, **kwargs):
        sourceKey = kwargs.get('sourceKey', 'text')
        if sourceKey in self.source:
            text = self.source[sourceKey]
        else:
            LOG_ERROR('Invalid source key', sourceKey)
            return ''
        if ctx is None:
            ctx = {}
        if type(self.ctx) is DictType and type(ctx) is DictType:
            ctx.update(self.ctx)
        if ctx:
            try:
                text = text % ctx
            except (ValueError, TypeError, KeyError):
                LOG_WARNING('Can not format template (source, ctx)', text, ctx)
                LOG_CURRENT_EXCEPTION()

        return text


class DummyTemplate(Template):

    def __repr__(self):
        return 'DummyTemplate(source = {0:>s})'.format(self.source)

    def format(self, ctx = None, **kwargs):
        return self.source


class Collection(defaultdict):

    def __init__(self, domain, ns):
        super(Collection, self).__init__()
        self._domain = domain
        self._ns = ns

    def __repr__(self):
        return 'Collection(domain = {0:>s}, ns = {1:>s}, keys = {2!r:s})'.format(self._domain, self._ns, self.keys())

    def __missing__(self, key):
        self[key] = value = DummyTemplate(key)
        return value

    def load(self, *args):
        raise NotImplementedError, 'Loader.load not implemented'

    def unload(self):
        self.clear()

    def _make(self, source):
        return Template(source)

    def format(self, key, ctx = None, **kwargs):
        return self[key].format(ctx=ctx, **kwargs)


class XMLCollection(Collection):

    def load(self, section = None, clear = False):
        if section is None:
            if clear:
                ResMgr.purge(self._domain)
            section = ResMgr.openSection(self._domain)
            if section is None:
                LOG_ERROR('{0:>s} can not open or read'.format(self._domain))
                return
        if len(self._ns):
            subsection = section[self._ns]
            if subsection is None:
                return
        else:
            subsection = section
        for key, child in subsection.items():
            self[key] = self._make(child)

        return

    def _make(self, source):
        keys = source.keys()
        ctx = None
        srcDict = {}
        if len(keys) > 0:
            for key in keys:
                if 'context' == key:
                    ctx = dict(map(lambda item: (item[0], item[1].asString), source['context'].items()))
                else:
                    srcDict[key] = html.translation(source.readString(key))

        else:
            srcDict['text'] = html.translation(source.asString)
        return Template(srcDict, ctx)
