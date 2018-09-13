# Embedded file name: scripts/client/helpers/feedparser.py
"""Universal feed parser

Handles RSS 0.9x, RSS 1.0, RSS 2.0, CDF, Atom 0.3, and Atom 1.0 feeds

Visit https://code.google.com/p/feedparser/ for the latest version
Visit http://packages.python.org/feedparser/ for the latest documentation

Required: Python 2.4 or later
Recommended: iconv_codec <http://cjkpython.i18n.org/>
"""
__version__ = '5.1.2'
__license__ = "\nCopyright (c) 2010-2012 Kurt McKee <contactme@kurtmckee.org>\nCopyright (c) 2002-2008 Mark Pilgrim\nAll rights reserved.\n\nRedistribution and use in source and binary forms, with or without modification,\nare permitted provided that the following conditions are met:\n\n* Redistributions of source code must retain the above copyright notice,\n  this list of conditions and the following disclaimer.\n* Redistributions in binary form must reproduce the above copyright notice,\n  this list of conditions and the following disclaimer in the documentation\n  and/or other materials provided with the distribution.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS'\nAND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE\nIMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE\nARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE\nLIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR\nCONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF\nSUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS\nINTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN\nCONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)\nARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE\nPOSSIBILITY OF SUCH DAMAGE."
__author__ = 'Mark Pilgrim <http://diveintomark.org/>'
__contributors__ = ['Jason Diamond <http://injektilo.org/>',
 'John Beimler <http://john.beimler.org/>',
 'Fazal Majid <http://www.majid.info/mylos/weblog/>',
 'Aaron Swartz <http://aaronsw.com/>',
 'Kevin Marks <http://epeus.blogspot.com/>',
 'Sam Ruby <http://intertwingly.net/>',
 'Ade Oshineye <http://blog.oshineye.com/>',
 'Martin Pool <http://sourcefrog.net/>',
 'Kurt McKee <http://kurtmckee.org/>']
USER_AGENT = 'UniversalFeedParser/%s +https://code.google.com/p/feedparser/' % __version__
ACCEPT_HEADER = 'application/atom+xml,application/rdf+xml,application/rss+xml,application/x-netcdf,application/xml;q=0.9,text/xml;q=0.2,*/*;q=0.1'
PREFERRED_XML_PARSERS = ['drv_libxml2']
TIDY_MARKUP = 0
PREFERRED_TIDY_INTERFACES = ['uTidy', 'mxTidy']
RESOLVE_RELATIVE_URIS = 1
SANITIZE_HTML = 1
PARSE_MICROFORMATS = 1
try:
    import rfc822
except ImportError:
    from email import _parseaddr as rfc822

try:
    _maketrans = bytes.maketrans
except (NameError, AttributeError):
    import string
    _maketrans = string.maketrans

try:
    import base64, binascii
except ImportError:
    base64 = binascii = None
else:
    _base64decode = getattr(base64, 'decodebytes', base64.decodestring)

try:
    if bytes is str:
        raise NameError
except NameError:

    def _s2bytes(s):
        return s


    def _l2bytes(l):
        return ''.join(map(chr, l))


else:

    def _s2bytes(s):
        return bytes(s, 'utf8')


    def _l2bytes(l):
        return bytes(l)


ACCEPTABLE_URI_SCHEMES = ('file',
 'ftp',
 'gopher',
 'h323',
 'hdl',
 'http',
 'https',
 'imap',
 'magnet',
 'mailto',
 'mms',
 'news',
 'nntp',
 'prospero',
 'rsync',
 'rtsp',
 'rtspu',
 'sftp',
 'shttp',
 'sip',
 'sips',
 'snews',
 'svn',
 'svn+ssh',
 'telnet',
 'wais',
 'aim',
 'callto',
 'cvs',
 'facetime',
 'feed',
 'git',
 'gtalk',
 'irc',
 'ircs',
 'irc6',
 'itms',
 'mms',
 'msnim',
 'skype',
 'ssh',
 'smb',
 'svn',
 'ymsg')
import cgi
import codecs
import copy
import datetime
import re
import struct
import time
import types
import urllib
import urllib2
import urlparse
import warnings
from htmlentitydefs import name2codepoint, codepoint2name, entitydefs
try:
    from io import BytesIO as _StringIO
except ImportError:
    try:
        from cStringIO import StringIO as _StringIO
    except ImportError:
        from StringIO import StringIO as _StringIO

try:
    import gzip
except ImportError:
    gzip = None

try:
    import zlib
except ImportError:
    zlib = None

try:
    import xml.sax
    from xml.sax.saxutils import escape as _xmlescape
except ImportError:
    _XML_AVAILABLE = 0

    def _xmlescape(data, entities = {}):
        data = data.replace('&', '&amp;')
        data = data.replace('>', '&gt;')
        data = data.replace('<', '&lt;')
        for char, entity in entities:
            data = data.replace(char, entity)

        return data


else:
    try:
        xml.sax.make_parser(PREFERRED_XML_PARSERS)
    except xml.sax.SAXReaderNotAvailable:
        _XML_AVAILABLE = 0
    else:
        _XML_AVAILABLE = 1

try:
    import sgmllib
except ImportError:
    _SGML_AVAILABLE = 0

    class sgmllib(object):

        class SGMLParser(object):

            def goahead(self, i):
                pass

            def parse_starttag(self, i):
                pass


else:
    _SGML_AVAILABLE = 1
    charref = re.compile('&#(\\d+|[xX][0-9a-fA-F]+);')
    tagfind = re.compile('[a-zA-Z][-_.:a-zA-Z0-9]*')
    attrfind = re.compile('\\s*([a-zA-Z_][-:.a-zA-Z_0-9]*)[$]?(\\s*=\\s*(\\\'[^\\\']*\\\'|"[^"]*"|[][\\-a-zA-Z0-9./,:;+*%?!&$\\(\\)_#=~\\\'"@]*))?')
    entityref = sgmllib.entityref
    incomplete = sgmllib.incomplete
    interesting = sgmllib.interesting
    shorttag = sgmllib.shorttag
    shorttagopen = sgmllib.shorttagopen
    starttagopen = sgmllib.starttagopen

    class _EndBracketRegEx():

        def __init__(self):
            self.endbracket = re.compile('([^\'"<>]|"[^"]*"(?=>|/|\\s|\\w+=)|\'[^\']*\'(?=>|/|\\s|\\w+=))*(?=[<>])|.*?(?=[<>])')

        def search(self, target, index = 0):
            match = self.endbracket.match(target, index)
            if match is not None:
                return EndBracketMatch(match)
            else:
                return


    class EndBracketMatch():

        def __init__(self, match):
            self.match = match

        def start(self, n):
            return self.match.end(n)


    endbracket = _EndBracketRegEx()

try:
    import iconv_codec
except ImportError:
    pass

try:
    import chardet
except ImportError:
    chardet = None

try:
    import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    PARSE_MICROFORMATS = False

try:
    codecs.lookup('utf_32')
except LookupError:
    _UTF32_AVAILABLE = False
else:
    _UTF32_AVAILABLE = True

class ThingsNobodyCaresAboutButMe(Exception):
    pass


class CharacterEncodingOverride(ThingsNobodyCaresAboutButMe):
    pass


class CharacterEncodingUnknown(ThingsNobodyCaresAboutButMe):
    pass


class NonXMLContentType(ThingsNobodyCaresAboutButMe):
    pass


class UndeclaredNamespace(Exception):
    pass


SUPPORTED_VERSIONS = {'': u'unknown',
 'rss090': u'RSS 0.90',
 'rss091n': u'RSS 0.91 (Netscape)',
 'rss091u': u'RSS 0.91 (Userland)',
 'rss092': u'RSS 0.92',
 'rss093': u'RSS 0.93',
 'rss094': u'RSS 0.94',
 'rss20': u'RSS 2.0',
 'rss10': u'RSS 1.0',
 'rss': u'RSS (unknown version)',
 'atom01': u'Atom 0.1',
 'atom02': u'Atom 0.2',
 'atom03': u'Atom 0.3',
 'atom10': u'Atom 1.0',
 'atom': u'Atom (unknown version)',
 'cdf': u'CDF'}

class FeedParserDict(dict):
    keymap = {'channel': 'feed',
     'items': 'entries',
     'guid': 'id',
     'date': 'updated',
     'date_parsed': 'updated_parsed',
     'description': ['summary', 'subtitle'],
     'description_detail': ['summary_detail', 'subtitle_detail'],
     'url': ['href'],
     'modified': 'updated',
     'modified_parsed': 'updated_parsed',
     'issued': 'published',
     'issued_parsed': 'published_parsed',
     'copyright': 'rights',
     'copyright_detail': 'rights_detail',
     'tagline': 'subtitle',
     'tagline_detail': 'subtitle_detail'}

    def __getitem__(self, key):
        if key == 'category':
            try:
                return dict.__getitem__(self, 'tags')[0]['term']
            except IndexError:
                raise KeyError, "object doesn't have key 'category'"

        else:
            if key == 'enclosures':
                norel = lambda link: FeedParserDict([ (name, value) for name, value in link.items() if name != 'rel' ])
                return [ norel(link) for link in dict.__getitem__(self, 'links') if link['rel'] == u'enclosure' ]
            if key == 'license':
                for link in dict.__getitem__(self, 'links'):
                    if link['rel'] == u'license' and 'href' in link:
                        return link['href']

            else:
                if key == 'updated':
                    if not dict.__contains__(self, 'updated') and dict.__contains__(self, 'published'):
                        warnings.warn("To avoid breaking existing software while fixing issue 310, a temporary mapping has been created from `updated` to `published` if `updated` doesn't exist. This fallback will be removed in a future version of feedparser.", DeprecationWarning)
                        return dict.__getitem__(self, 'published')
                    return dict.__getitem__(self, 'updated')
                if key == 'updated_parsed':
                    if not dict.__contains__(self, 'updated_parsed') and dict.__contains__(self, 'published_parsed'):
                        warnings.warn("To avoid breaking existing software while fixing issue 310, a temporary mapping has been created from `updated_parsed` to `published_parsed` if `updated_parsed` doesn't exist. This fallback will be removed in a future version of feedparser.", DeprecationWarning)
                        return dict.__getitem__(self, 'published_parsed')
                    return dict.__getitem__(self, 'updated_parsed')
                realkey = self.keymap.get(key, key)
                if isinstance(realkey, list):
                    for k in realkey:
                        if dict.__contains__(self, k):
                            return dict.__getitem__(self, k)

                elif dict.__contains__(self, realkey):
                    return dict.__getitem__(self, realkey)
        return dict.__getitem__(self, key)

    def __contains__(self, key):
        if key in ('updated', 'updated_parsed'):
            return dict.__contains__(self, key)
        else:
            try:
                self.__getitem__(key)
            except KeyError:
                return False

            return True

    has_key = __contains__

    def get(self, key, default = None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __setitem__(self, key, value):
        key = self.keymap.get(key, key)
        if isinstance(key, list):
            key = key[0]
        return dict.__setitem__(self, key, value)

    def setdefault(self, key, value):
        if key not in self:
            self[key] = value
            return value
        return self[key]

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError, "object has no attribute '%s'" % key

    def __hash__(self):
        return id(self)


_cp1252 = {128: unichr(8364),
 130: unichr(8218),
 131: unichr(402),
 132: unichr(8222),
 133: unichr(8230),
 134: unichr(8224),
 135: unichr(8225),
 136: unichr(710),
 137: unichr(8240),
 138: unichr(352),
 139: unichr(8249),
 140: unichr(338),
 142: unichr(381),
 145: unichr(8216),
 146: unichr(8217),
 147: unichr(8220),
 148: unichr(8221),
 149: unichr(8226),
 150: unichr(8211),
 151: unichr(8212),
 152: unichr(732),
 153: unichr(8482),
 154: unichr(353),
 155: unichr(8250),
 156: unichr(339),
 158: unichr(382),
 159: unichr(376)}
_urifixer = re.compile('^([A-Za-z][A-Za-z0-9+-.]*://)(/*)(.*?)')

def _urljoin(base, uri):
    uri = _urifixer.sub('\\1\\3', uri)
    if not isinstance(uri, unicode):
        uri = uri.decode('utf-8', 'ignore')
    uri = urlparse.urljoin(base, uri)
    if not isinstance(uri, unicode):
        return uri.decode('utf-8', 'ignore')
    return uri


class _FeedParserMixin():
    namespaces = {'': '',
     'http://backend.userland.com/rss': '',
     'http://blogs.law.harvard.edu/tech/rss': '',
     'http://purl.org/rss/1.0/': '',
     'http://my.netscape.com/rdf/simple/0.9/': '',
     'http://example.com/newformat#': '',
     'http://example.com/necho': '',
     'http://purl.org/echo/': '',
     'uri/of/echo/namespace#': '',
     'http://purl.org/pie/': '',
     'http://purl.org/atom/ns#': '',
     'http://www.w3.org/2005/Atom': '',
     'http://purl.org/rss/1.0/modules/rss091#': '',
     'http://webns.net/mvcb/': 'admin',
     'http://purl.org/rss/1.0/modules/aggregation/': 'ag',
     'http://purl.org/rss/1.0/modules/annotate/': 'annotate',
     'http://media.tangent.org/rss/1.0/': 'audio',
     'http://backend.userland.com/blogChannelModule': 'blogChannel',
     'http://web.resource.org/cc/': 'cc',
     'http://backend.userland.com/creativeCommonsRssModule': 'creativeCommons',
     'http://purl.org/rss/1.0/modules/company': 'co',
     'http://purl.org/rss/1.0/modules/content/': 'content',
     'http://my.theinfo.org/changed/1.0/rss/': 'cp',
     'http://purl.org/dc/elements/1.1/': 'dc',
     'http://purl.org/dc/terms/': 'dcterms',
     'http://purl.org/rss/1.0/modules/email/': 'email',
     'http://purl.org/rss/1.0/modules/event/': 'ev',
     'http://rssnamespace.org/feedburner/ext/1.0': 'feedburner',
     'http://freshmeat.net/rss/fm/': 'fm',
     'http://xmlns.com/foaf/0.1/': 'foaf',
     'http://www.w3.org/2003/01/geo/wgs84_pos#': 'geo',
     'http://postneo.com/icbm/': 'icbm',
     'http://purl.org/rss/1.0/modules/image/': 'image',
     'http://www.itunes.com/DTDs/PodCast-1.0.dtd': 'itunes',
     'http://example.com/DTDs/PodCast-1.0.dtd': 'itunes',
     'http://purl.org/rss/1.0/modules/link/': 'l',
     'http://search.yahoo.com/mrss': 'media',
     'http://search.yahoo.com/mrss/': 'media',
     'http://madskills.com/public/xml/rss/module/pingback/': 'pingback',
     'http://prismstandard.org/namespaces/1.2/basic/': 'prism',
     'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
     'http://www.w3.org/2000/01/rdf-schema#': 'rdfs',
     'http://purl.org/rss/1.0/modules/reference/': 'ref',
     'http://purl.org/rss/1.0/modules/richequiv/': 'reqv',
     'http://purl.org/rss/1.0/modules/search/': 'search',
     'http://purl.org/rss/1.0/modules/slash/': 'slash',
     'http://schemas.xmlsoap.org/soap/envelope/': 'soap',
     'http://purl.org/rss/1.0/modules/servicestatus/': 'ss',
     'http://hacks.benhammersley.com/rss/streaming/': 'str',
     'http://purl.org/rss/1.0/modules/subscription/': 'sub',
     'http://purl.org/rss/1.0/modules/syndication/': 'sy',
     'http://schemas.pocketsoap.com/rss/myDescModule/': 'szf',
     'http://purl.org/rss/1.0/modules/taxonomy/': 'taxo',
     'http://purl.org/rss/1.0/modules/threading/': 'thr',
     'http://purl.org/rss/1.0/modules/textinput/': 'ti',
     'http://madskills.com/public/xml/rss/module/trackback/': 'trackback',
     'http://wellformedweb.org/commentAPI/': 'wfw',
     'http://purl.org/rss/1.0/modules/wiki/': 'wiki',
     'http://www.w3.org/1999/xhtml': 'xhtml',
     'http://www.w3.org/1999/xlink': 'xlink',
     'http://www.w3.org/XML/1998/namespace': 'xml'}
    _matchnamespaces = {}
    can_be_relative_uri = set(['link',
     'id',
     'wfw_comment',
     'wfw_commentrss',
     'docs',
     'url',
     'href',
     'comments',
     'icon',
     'logo'])
    can_contain_relative_uris = set(['content',
     'title',
     'summary',
     'info',
     'tagline',
     'subtitle',
     'copyright',
     'rights',
     'description'])
    can_contain_dangerous_markup = set(['content',
     'title',
     'summary',
     'info',
     'tagline',
     'subtitle',
     'copyright',
     'rights',
     'description'])
    html_types = [u'text/html', u'application/xhtml+xml']

    def __init__(self, baseuri = None, baselang = None, encoding = u'utf-8'):
        if not self._matchnamespaces:
            for k, v in self.namespaces.items():
                self._matchnamespaces[k.lower()] = v

        self.feeddata = FeedParserDict()
        self.encoding = encoding
        self.entries = []
        self.version = u''
        self.namespacesInUse = {}
        self.infeed = 0
        self.inentry = 0
        self.incontent = 0
        self.intextinput = 0
        self.inimage = 0
        self.inauthor = 0
        self.incontributor = 0
        self.inpublisher = 0
        self.insource = 0
        self.sourcedata = FeedParserDict()
        self.contentparams = FeedParserDict()
        self._summaryKey = None
        self.namespacemap = {}
        self.elementstack = []
        self.basestack = []
        self.langstack = []
        self.baseuri = baseuri or u''
        self.lang = baselang or None
        self.svgOK = 0
        self.title_depth = -1
        self.depth = 0
        if baselang:
            self.feeddata['language'] = baselang.replace('_', '-')
        self.property_depth_map = {}
        return

    def _normalize_attributes(self, kv):
        k = kv[0].lower()
        v = k in ('rel', 'type') and kv[1].lower() or kv[1]
        if isinstance(self, _LooseFeedParser):
            v = v.replace('&amp;', '&')
            if not isinstance(v, unicode):
                v = v.decode('utf-8')
        return (k, v)

    def unknown_starttag(self, tag, attrs):
        self.depth += 1
        attrs = map(self._normalize_attributes, attrs)
        attrsD = dict(attrs)
        baseuri = attrsD.get('xml:base', attrsD.get('base')) or self.baseuri
        if not isinstance(baseuri, unicode):
            baseuri = baseuri.decode(self.encoding, 'ignore')
        if self.baseuri:
            self.baseuri = _makeSafeAbsoluteURI(self.baseuri, baseuri) or self.baseuri
        else:
            self.baseuri = _urljoin(self.baseuri, baseuri)
        lang = attrsD.get('xml:lang', attrsD.get('lang'))
        if lang == '':
            lang = None
        elif lang is None:
            lang = self.lang
        if lang:
            if tag in ('feed', 'rss', 'rdf:RDF'):
                self.feeddata['language'] = lang.replace('_', '-')
        self.lang = lang
        self.basestack.append(self.baseuri)
        self.langstack.append(lang)
        for prefix, uri in attrs:
            if prefix.startswith('xmlns:'):
                self.trackNamespace(prefix[6:], uri)
            elif prefix == 'xmlns':
                self.trackNamespace(None, uri)

        if self.incontent and not self.contentparams.get('type', u'xml').endswith(u'xml'):
            if tag in ('xhtml:div', 'div'):
                return
            self.contentparams['type'] = u'application/xhtml+xml'
        if self.incontent and self.contentparams.get('type') == u'application/xhtml+xml':
            if tag.find(':') != -1:
                prefix, tag = tag.split(':', 1)
                namespace = self.namespacesInUse.get(prefix, '')
                if tag == 'math' and namespace == 'http://www.w3.org/1998/Math/MathML':
                    attrs.append(('xmlns', namespace))
                if tag == 'svg' and namespace == 'http://www.w3.org/2000/svg':
                    attrs.append(('xmlns', namespace))
            if tag == 'svg':
                self.svgOK += 1
            return self.handle_data('<%s%s>' % (tag, self.strattrs(attrs)), escape=0)
        else:
            if tag.find(':') != -1:
                prefix, suffix = tag.split(':', 1)
            else:
                prefix, suffix = '', tag
            prefix = self.namespacemap.get(prefix, prefix)
            if prefix:
                prefix = prefix + '_'
            if not prefix and tag not in ('title', 'link', 'description', 'name'):
                self.intextinput = 0
            if not prefix and tag not in ('title', 'link', 'description', 'url', 'href', 'width', 'height'):
                self.inimage = 0
            methodname = '_start_' + prefix + suffix
            try:
                method = getattr(self, methodname)
                return method(attrsD)
            except AttributeError:
                unknown_tag = prefix + suffix
                if len(attrsD) == 0:
                    return self.push(unknown_tag, 1)
                context = self._getContext()
                context[unknown_tag] = attrsD

            return

    def unknown_endtag(self, tag):
        if tag.find(':') != -1:
            prefix, suffix = tag.split(':', 1)
        else:
            prefix, suffix = '', tag
        prefix = self.namespacemap.get(prefix, prefix)
        if prefix:
            prefix = prefix + '_'
        if suffix == 'svg' and self.svgOK:
            self.svgOK -= 1
        methodname = '_end_' + prefix + suffix
        try:
            if self.svgOK:
                raise AttributeError()
            method = getattr(self, methodname)
            method()
        except AttributeError:
            self.pop(prefix + suffix)

        if self.incontent and not self.contentparams.get('type', u'xml').endswith(u'xml'):
            if tag in ('xhtml:div', 'div'):
                return
            self.contentparams['type'] = u'application/xhtml+xml'
        if self.incontent and self.contentparams.get('type') == u'application/xhtml+xml':
            tag = tag.split(':')[-1]
            self.handle_data('</%s>' % tag, escape=0)
        if self.basestack:
            self.basestack.pop()
            if self.basestack and self.basestack[-1]:
                self.baseuri = self.basestack[-1]
        if self.langstack:
            self.langstack.pop()
            if self.langstack:
                self.lang = self.langstack[-1]
        self.depth -= 1

    def handle_charref(self, ref):
        if not self.elementstack:
            return
        ref = ref.lower()
        if ref in ('34', '38', '39', '60', '62', 'x22', 'x26', 'x27', 'x3c', 'x3e'):
            text = '&#%s;' % ref
        else:
            if ref[0] == 'x':
                c = int(ref[1:], 16)
            else:
                c = int(ref)
            text = unichr(c).encode('utf-8')
        self.elementstack[-1][2].append(text)

    def handle_entityref(self, ref):
        if not self.elementstack:
            return
        if ref in ('lt', 'gt', 'quot', 'amp', 'apos'):
            text = '&%s;' % ref
        elif ref in self.entities:
            text = self.entities[ref]
            if text.startswith('&#') and text.endswith(';'):
                return self.handle_entityref(text)
        else:
            try:
                name2codepoint[ref]
            except KeyError:
                text = '&%s;' % ref
            else:
                text = unichr(name2codepoint[ref]).encode('utf-8')

        self.elementstack[-1][2].append(text)

    def handle_data(self, text, escape = 1):
        if not self.elementstack:
            return
        if escape and self.contentparams.get('type') == u'application/xhtml+xml':
            text = _xmlescape(text)
        self.elementstack[-1][2].append(text)

    def handle_comment(self, text):
        pass

    def handle_pi(self, text):
        pass

    def handle_decl(self, text):
        pass

    def parse_declaration(self, i):
        if self.rawdata[i:i + 9] == '<![CDATA[':
            k = self.rawdata.find(']]>', i)
            if k == -1:
                k = len(self.rawdata)
                return k
            self.handle_data(_xmlescape(self.rawdata[i + 9:k]), 0)
            return k + 3
        else:
            k = self.rawdata.find('>', i)
            if k >= 0:
                return k + 1
            return k

    def mapContentType(self, contentType):
        contentType = contentType.lower()
        if contentType == 'text' or contentType == 'plain':
            contentType = u'text/plain'
        elif contentType == 'html':
            contentType = u'text/html'
        elif contentType == 'xhtml':
            contentType = u'application/xhtml+xml'
        return contentType

    def trackNamespace(self, prefix, uri):
        loweruri = uri.lower()
        if not self.version:
            if (prefix, loweruri) == (None, 'http://my.netscape.com/rdf/simple/0.9/'):
                self.version = u'rss090'
            elif loweruri == 'http://purl.org/rss/1.0/':
                self.version = u'rss10'
            elif loweruri == 'http://www.w3.org/2005/atom':
                self.version = u'atom10'
        if loweruri.find(u'backend.userland.com/rss') != -1:
            uri = u'http://backend.userland.com/rss'
            loweruri = uri
        if loweruri in self._matchnamespaces:
            self.namespacemap[prefix] = self._matchnamespaces[loweruri]
            self.namespacesInUse[self._matchnamespaces[loweruri]] = uri
        else:
            self.namespacesInUse[prefix or ''] = uri
        return None

    def resolveURI(self, uri):
        return _urljoin(self.baseuri or u'', uri)

    def decodeEntities(self, element, data):
        return data

    def strattrs(self, attrs):
        return ''.join([ ' %s="%s"' % (t[0], _xmlescape(t[1], {'"': '&quot;'})) for t in attrs ])

    def push(self, element, expectingText):
        self.elementstack.append([element, expectingText, []])

    def pop(self, element, stripWhitespace = 1):
        if not self.elementstack:
            return
        elif self.elementstack[-1][0] != element:
            return
        else:
            element, expectingText, pieces = self.elementstack.pop()
            if self.version == u'atom10' and self.contentparams.get('type', u'text') == u'application/xhtml+xml':
                while pieces and len(pieces) > 1 and not pieces[-1].strip():
                    del pieces[-1]

                while pieces and len(pieces) > 1 and not pieces[0].strip():
                    del pieces[0]

                if pieces and (pieces[0] == '<div>' or pieces[0].startswith('<div ')) and pieces[-1] == '</div>':
                    depth = 0
                    for piece in pieces[:-1]:
                        if piece.startswith('</'):
                            depth -= 1
                            if depth == 0:
                                break
                        elif piece.startswith('<') and not piece.endswith('/>'):
                            depth += 1
                    else:
                        pieces = pieces[1:-1]

            for i, v in enumerate(pieces):
                if not isinstance(v, unicode):
                    pieces[i] = v.decode('utf-8')

            output = u''.join(pieces)
            if stripWhitespace:
                output = output.strip()
            if not expectingText:
                return output
            if base64 and self.contentparams.get('base64', 0):
                try:
                    output = _base64decode(output)
                except binascii.Error:
                    pass
                except binascii.Incomplete:
                    pass
                except TypeError:
                    output = _base64decode(output.encode('utf-8')).decode('utf-8')

            if element in self.can_be_relative_uri and output:
                output = self.resolveURI(output)
            if not self.contentparams.get('base64', 0):
                output = self.decodeEntities(element, output)
            if not self.version.startswith(u'atom') and self.contentparams.get('type') == u'text/plain':
                if self.lookslikehtml(output):
                    self.contentparams['type'] = u'text/html'
            try:
                del self.contentparams['mode']
            except KeyError:
                pass

            try:
                del self.contentparams['base64']
            except KeyError:
                pass

            is_htmlish = self.mapContentType(self.contentparams.get('type', u'text/html')) in self.html_types
            if is_htmlish and RESOLVE_RELATIVE_URIS:
                if element in self.can_contain_relative_uris:
                    output = _resolveRelativeURIs(output, self.baseuri, self.encoding, self.contentparams.get('type', u'text/html'))
            if PARSE_MICROFORMATS and is_htmlish and element in ('content', 'description', 'summary'):
                mfresults = _parseMicroformats(output, self.baseuri, self.encoding)
                if mfresults:
                    for tag in mfresults.get('tags', []):
                        self._addTag(tag['term'], tag['scheme'], tag['label'])

                    for enclosure in mfresults.get('enclosures', []):
                        self._start_enclosure(enclosure)

                    for xfn in mfresults.get('xfn', []):
                        self._addXFN(xfn['relationships'], xfn['href'], xfn['name'])

                    vcard = mfresults.get('vcard')
                    if vcard:
                        self._getContext()['vcard'] = vcard
            if is_htmlish and SANITIZE_HTML:
                if element in self.can_contain_dangerous_markup:
                    output = _sanitizeHTML(output, self.encoding, self.contentparams.get('type', u'text/html'))
            if self.encoding and not isinstance(output, unicode):
                output = output.decode(self.encoding, 'ignore')
            if self.encoding in (u'utf-8', u'utf-8_INVALID_PYTHON_3') and isinstance(output, unicode):
                try:
                    output = output.encode('iso-8859-1').decode('utf-8')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    pass

            if isinstance(output, unicode):
                output = output.translate(_cp1252)
            if element == 'category':
                return output
            elif element == 'title' and -1 < self.title_depth <= self.depth:
                return output
            if self.inentry and not self.insource:
                if element == 'content':
                    self.entries[-1].setdefault(element, [])
                    contentparams = copy.deepcopy(self.contentparams)
                    contentparams['value'] = output
                    self.entries[-1][element].append(contentparams)
                elif element == 'link':
                    if not self.inimage:
                        output = re.sub('&([A-Za-z0-9_]+);', '&\\g<1>', output)
                        self.entries[-1][element] = output
                        if output:
                            self.entries[-1]['links'][-1]['href'] = output
                else:
                    if element == 'description':
                        element = 'summary'
                    old_value_depth = self.property_depth_map.setdefault(self.entries[-1], {}).get(element)
                    if old_value_depth is None or self.depth <= old_value_depth:
                        self.property_depth_map[self.entries[-1]][element] = self.depth
                        self.entries[-1][element] = output
                    if self.incontent:
                        contentparams = copy.deepcopy(self.contentparams)
                        contentparams['value'] = output
                        self.entries[-1][element + '_detail'] = contentparams
            elif self.infeed or self.insource:
                context = self._getContext()
                if element == 'description':
                    element = 'subtitle'
                context[element] = output
                if element == 'link':
                    output = re.sub('&([A-Za-z0-9_]+);', '&\\g<1>', output)
                    context[element] = output
                    context['links'][-1]['href'] = output
                elif self.incontent:
                    contentparams = copy.deepcopy(self.contentparams)
                    contentparams['value'] = output
                    context[element + '_detail'] = contentparams
            return output

    def pushContent(self, tag, attrsD, defaultContentType, expectingText):
        self.incontent += 1
        if self.lang:
            self.lang = self.lang.replace('_', '-')
        self.contentparams = FeedParserDict({'type': self.mapContentType(attrsD.get('type', defaultContentType)),
         'language': self.lang,
         'base': self.baseuri})
        self.contentparams['base64'] = self._isBase64(attrsD, self.contentparams)
        self.push(tag, expectingText)

    def popContent(self, tag):
        value = self.pop(tag)
        self.incontent -= 1
        self.contentparams.clear()
        return value

    @staticmethod
    def lookslikehtml(s):
        if not (re.search('</(\\w+)>', s) or re.search('&#?\\w+;', s)):
            return
        if filter(lambda t: t.lower() not in _HTMLSanitizer.acceptable_elements, re.findall('</?(\\w+)', s)):
            return
        if filter(lambda e: e not in entitydefs.keys(), re.findall('&(\\w+);', s)):
            return
        return 1

    def _mapToStandardPrefix(self, name):
        colonpos = name.find(':')
        if colonpos != -1:
            prefix = name[:colonpos]
            suffix = name[colonpos + 1:]
            prefix = self.namespacemap.get(prefix, prefix)
            name = prefix + ':' + suffix
        return name

    def _getAttribute(self, attrsD, name):
        return attrsD.get(self._mapToStandardPrefix(name))

    def _isBase64(self, attrsD, contentparams):
        if attrsD.get('mode', '') == 'base64':
            return 1
        if self.contentparams['type'].startswith(u'text/'):
            return 0
        if self.contentparams['type'].endswith(u'+xml'):
            return 0
        if self.contentparams['type'].endswith(u'/xml'):
            return 0
        return 1

    def _itsAnHrefDamnIt(self, attrsD):
        href = attrsD.get('url', attrsD.get('uri', attrsD.get('href', None)))
        if href:
            try:
                del attrsD['url']
            except KeyError:
                pass

            try:
                del attrsD['uri']
            except KeyError:
                pass

            attrsD['href'] = href
        return attrsD

    def _save(self, key, value, overwrite = False):
        context = self._getContext()
        if overwrite:
            context[key] = value
        else:
            context.setdefault(key, value)

    def _start_rss(self, attrsD):
        versionmap = {'0.91': u'rss091u',
         '0.92': u'rss092',
         '0.93': u'rss093',
         '0.94': u'rss094'}
        if not self.version or not self.version.startswith(u'rss'):
            attr_version = attrsD.get('version', '')
            version = versionmap.get(attr_version)
            if version:
                self.version = version
            elif attr_version.startswith('2.'):
                self.version = u'rss20'
            else:
                self.version = u'rss'

    def _start_channel(self, attrsD):
        self.infeed = 1
        self._cdf_common(attrsD)

    def _cdf_common(self, attrsD):
        if 'lastmod' in attrsD:
            self._start_modified({})
            self.elementstack[-1][-1] = attrsD['lastmod']
            self._end_modified()
        if 'href' in attrsD:
            self._start_link({})
            self.elementstack[-1][-1] = attrsD['href']
            self._end_link()

    def _start_feed(self, attrsD):
        self.infeed = 1
        versionmap = {'0.1': u'atom01',
         '0.2': u'atom02',
         '0.3': u'atom03'}
        if not self.version:
            attr_version = attrsD.get('version')
            version = versionmap.get(attr_version)
            if version:
                self.version = version
            else:
                self.version = u'atom'

    def _end_channel(self):
        self.infeed = 0

    _end_feed = _end_channel

    def _start_image(self, attrsD):
        context = self._getContext()
        if not self.inentry:
            context.setdefault('image', FeedParserDict())
        self.inimage = 1
        self.title_depth = -1
        self.push('image', 0)

    def _end_image(self):
        self.pop('image')
        self.inimage = 0

    def _start_textinput(self, attrsD):
        context = self._getContext()
        context.setdefault('textinput', FeedParserDict())
        self.intextinput = 1
        self.title_depth = -1
        self.push('textinput', 0)

    _start_textInput = _start_textinput

    def _end_textinput(self):
        self.pop('textinput')
        self.intextinput = 0

    _end_textInput = _end_textinput

    def _start_author(self, attrsD):
        self.inauthor = 1
        self.push('author', 1)
        context = self._getContext()
        context.setdefault('authors', [])
        context['authors'].append(FeedParserDict())

    _start_managingeditor = _start_author
    _start_dc_author = _start_author
    _start_dc_creator = _start_author
    _start_itunes_author = _start_author

    def _end_author(self):
        self.pop('author')
        self.inauthor = 0
        self._sync_author_detail()

    _end_managingeditor = _end_author
    _end_dc_author = _end_author
    _end_dc_creator = _end_author
    _end_itunes_author = _end_author

    def _start_itunes_owner(self, attrsD):
        self.inpublisher = 1
        self.push('publisher', 0)

    def _end_itunes_owner(self):
        self.pop('publisher')
        self.inpublisher = 0
        self._sync_author_detail('publisher')

    def _start_contributor(self, attrsD):
        self.incontributor = 1
        context = self._getContext()
        context.setdefault('contributors', [])
        context['contributors'].append(FeedParserDict())
        self.push('contributor', 0)

    def _end_contributor(self):
        self.pop('contributor')
        self.incontributor = 0

    def _start_dc_contributor(self, attrsD):
        self.incontributor = 1
        context = self._getContext()
        context.setdefault('contributors', [])
        context['contributors'].append(FeedParserDict())
        self.push('name', 0)

    def _end_dc_contributor(self):
        self._end_name()
        self.incontributor = 0

    def _start_name(self, attrsD):
        self.push('name', 0)

    _start_itunes_name = _start_name

    def _end_name(self):
        value = self.pop('name')
        if self.inpublisher:
            self._save_author('name', value, 'publisher')
        elif self.inauthor:
            self._save_author('name', value)
        elif self.incontributor:
            self._save_contributor('name', value)
        elif self.intextinput:
            context = self._getContext()
            context['name'] = value

    _end_itunes_name = _end_name

    def _start_width(self, attrsD):
        self.push('width', 0)

    def _end_width(self):
        value = self.pop('width')
        try:
            value = int(value)
        except ValueError:
            value = 0

        if self.inimage:
            context = self._getContext()
            context['width'] = value

    def _start_height(self, attrsD):
        self.push('height', 0)

    def _end_height(self):
        value = self.pop('height')
        try:
            value = int(value)
        except ValueError:
            value = 0

        if self.inimage:
            context = self._getContext()
            context['height'] = value

    def _start_url(self, attrsD):
        self.push('href', 1)

    _start_homepage = _start_url
    _start_uri = _start_url

    def _end_url(self):
        value = self.pop('href')
        if self.inauthor:
            self._save_author('href', value)
        elif self.incontributor:
            self._save_contributor('href', value)

    _end_homepage = _end_url
    _end_uri = _end_url

    def _start_email(self, attrsD):
        self.push('email', 0)

    _start_itunes_email = _start_email

    def _end_email(self):
        value = self.pop('email')
        if self.inpublisher:
            self._save_author('email', value, 'publisher')
        elif self.inauthor:
            self._save_author('email', value)
        elif self.incontributor:
            self._save_contributor('email', value)

    _end_itunes_email = _end_email

    def _getContext(self):
        if self.insource:
            context = self.sourcedata
        elif self.inimage and 'image' in self.feeddata:
            context = self.feeddata['image']
        elif self.intextinput:
            context = self.feeddata['textinput']
        elif self.inentry:
            context = self.entries[-1]
        else:
            context = self.feeddata
        return context

    def _save_author(self, key, value, prefix = 'author'):
        context = self._getContext()
        context.setdefault(prefix + '_detail', FeedParserDict())
        context[prefix + '_detail'][key] = value
        self._sync_author_detail()
        context.setdefault('authors', [FeedParserDict()])
        context['authors'][-1][key] = value

    def _save_contributor(self, key, value):
        context = self._getContext()
        context.setdefault('contributors', [FeedParserDict()])
        context['contributors'][-1][key] = value

    def _sync_author_detail(self, key = 'author'):
        context = self._getContext()
        detail = context.get('%s_detail' % key)
        if detail:
            name = detail.get('name')
            email = detail.get('email')
            if name and email:
                context[key] = u'%s (%s)' % (name, email)
            elif name:
                context[key] = name
            elif email:
                context[key] = email
        else:
            author, email = context.get(key), None
            if not author:
                return
            emailmatch = re.search(u'(([a-zA-Z0-9\\_\\-\\.\\+]+)@((\\[[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.)|(([a-zA-Z0-9\\-]+\\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?))(\\?subject=\\S+)?', author)
            if emailmatch:
                email = emailmatch.group(0)
                author = author.replace(email, u'')
                author = author.replace(u'()', u'')
                author = author.replace(u'<>', u'')
                author = author.replace(u'&lt;&gt;', u'')
                author = author.strip()
                if author and author[0] == u'(':
                    author = author[1:]
                if author and author[-1] == u')':
                    author = author[:-1]
                author = author.strip()
            if author or email:
                context.setdefault('%s_detail' % key, FeedParserDict())
            if author:
                context['%s_detail' % key]['name'] = author
            if email:
                context['%s_detail' % key]['email'] = email
        return

    def _start_subtitle(self, attrsD):
        self.pushContent('subtitle', attrsD, u'text/plain', 1)

    _start_tagline = _start_subtitle
    _start_itunes_subtitle = _start_subtitle

    def _end_subtitle(self):
        self.popContent('subtitle')

    _end_tagline = _end_subtitle
    _end_itunes_subtitle = _end_subtitle

    def _start_rights(self, attrsD):
        self.pushContent('rights', attrsD, u'text/plain', 1)

    _start_dc_rights = _start_rights
    _start_copyright = _start_rights

    def _end_rights(self):
        self.popContent('rights')

    _end_dc_rights = _end_rights
    _end_copyright = _end_rights

    def _start_item(self, attrsD):
        self.entries.append(FeedParserDict())
        self.push('item', 0)
        self.inentry = 1
        self.guidislink = 0
        self.title_depth = -1
        id = self._getAttribute(attrsD, 'rdf:about')
        if id:
            context = self._getContext()
            context['id'] = id
        self._cdf_common(attrsD)

    _start_entry = _start_item

    def _end_item(self):
        self.pop('item')
        self.inentry = 0

    _end_entry = _end_item

    def _start_dc_language(self, attrsD):
        self.push('language', 1)

    _start_language = _start_dc_language

    def _end_dc_language(self):
        self.lang = self.pop('language')

    _end_language = _end_dc_language

    def _start_dc_publisher(self, attrsD):
        self.push('publisher', 1)

    _start_webmaster = _start_dc_publisher

    def _end_dc_publisher(self):
        self.pop('publisher')
        self._sync_author_detail('publisher')

    _end_webmaster = _end_dc_publisher

    def _start_published(self, attrsD):
        self.push('published', 1)

    _start_dcterms_issued = _start_published
    _start_issued = _start_published
    _start_pubdate = _start_published

    def _end_published(self):
        value = self.pop('published')
        self._save('published_parsed', _parse_date(value), overwrite=True)

    _end_dcterms_issued = _end_published
    _end_issued = _end_published
    _end_pubdate = _end_published

    def _start_updated(self, attrsD):
        self.push('updated', 1)

    _start_modified = _start_updated
    _start_dcterms_modified = _start_updated
    _start_dc_date = _start_updated
    _start_lastbuilddate = _start_updated

    def _end_updated(self):
        value = self.pop('updated')
        parsed_value = _parse_date(value)
        self._save('updated_parsed', parsed_value, overwrite=True)

    _end_modified = _end_updated
    _end_dcterms_modified = _end_updated
    _end_dc_date = _end_updated
    _end_lastbuilddate = _end_updated

    def _start_created(self, attrsD):
        self.push('created', 1)

    _start_dcterms_created = _start_created

    def _end_created(self):
        value = self.pop('created')
        self._save('created_parsed', _parse_date(value), overwrite=True)

    _end_dcterms_created = _end_created

    def _start_expirationdate(self, attrsD):
        self.push('expired', 1)

    def _end_expirationdate(self):
        self._save('expired_parsed', _parse_date(self.pop('expired')), overwrite=True)

    def _start_cc_license(self, attrsD):
        context = self._getContext()
        value = self._getAttribute(attrsD, 'rdf:resource')
        attrsD = FeedParserDict()
        attrsD['rel'] = u'license'
        if value:
            attrsD['href'] = value
        context.setdefault('links', []).append(attrsD)

    def _start_creativecommons_license(self, attrsD):
        self.push('license', 1)

    _start_creativeCommons_license = _start_creativecommons_license

    def _end_creativecommons_license(self):
        value = self.pop('license')
        context = self._getContext()
        attrsD = FeedParserDict()
        attrsD['rel'] = u'license'
        if value:
            attrsD['href'] = value
        context.setdefault('links', []).append(attrsD)
        del context['license']

    _end_creativeCommons_license = _end_creativecommons_license

    def _addXFN(self, relationships, href, name):
        context = self._getContext()
        xfn = context.setdefault('xfn', [])
        value = FeedParserDict({'relationships': relationships,
         'href': href,
         'name': name})
        if value not in xfn:
            xfn.append(value)

    def _addTag(self, term, scheme, label):
        context = self._getContext()
        tags = context.setdefault('tags', [])
        if not term and not scheme and not label:
            return
        value = FeedParserDict({'term': term,
         'scheme': scheme,
         'label': label})
        if value not in tags:
            tags.append(value)

    def _start_category(self, attrsD):
        term = attrsD.get('term')
        scheme = attrsD.get('scheme', attrsD.get('domain'))
        label = attrsD.get('label')
        self._addTag(term, scheme, label)
        self.push('category', 1)

    _start_dc_subject = _start_category
    _start_keywords = _start_category

    def _start_media_category(self, attrsD):
        attrsD.setdefault('scheme', u'http://search.yahoo.com/mrss/category_schema')
        self._start_category(attrsD)

    def _end_itunes_keywords(self):
        for term in self.pop('itunes_keywords').split(','):
            if term.strip():
                self._addTag(term.strip(), u'http://www.itunes.com/', None)

        return

    def _start_itunes_category(self, attrsD):
        self._addTag(attrsD.get('text'), u'http://www.itunes.com/', None)
        self.push('category', 1)
        return

    def _end_category(self):
        value = self.pop('category')
        if not value:
            return
        else:
            context = self._getContext()
            tags = context['tags']
            if value and len(tags) and not tags[-1]['term']:
                tags[-1]['term'] = value
            else:
                self._addTag(value, None, None)
            return

    _end_dc_subject = _end_category
    _end_keywords = _end_category
    _end_itunes_category = _end_category
    _end_media_category = _end_category

    def _start_cloud(self, attrsD):
        self._getContext()['cloud'] = FeedParserDict(attrsD)

    def _start_link(self, attrsD):
        attrsD.setdefault('rel', u'alternate')
        if attrsD['rel'] == u'self':
            attrsD.setdefault('type', u'application/atom+xml')
        else:
            attrsD.setdefault('type', u'text/html')
        context = self._getContext()
        attrsD = self._itsAnHrefDamnIt(attrsD)
        if 'href' in attrsD:
            attrsD['href'] = self.resolveURI(attrsD['href'])
        expectingText = self.infeed or self.inentry or self.insource
        context.setdefault('links', [])
        if not (self.inentry and self.inimage):
            context['links'].append(FeedParserDict(attrsD))
        if 'href' in attrsD:
            expectingText = 0
            if attrsD.get('rel') == u'alternate' and self.mapContentType(attrsD.get('type')) in self.html_types:
                context['link'] = attrsD['href']
        else:
            self.push('link', expectingText)

    def _end_link(self):
        value = self.pop('link')

    def _start_guid(self, attrsD):
        self.guidislink = attrsD.get('ispermalink', 'true') == 'true'
        self.push('id', 1)

    _start_id = _start_guid

    def _end_guid(self):
        value = self.pop('id')
        self._save('guidislink', self.guidislink and 'link' not in self._getContext())
        if self.guidislink:
            self._save('link', value)

    _end_id = _end_guid

    def _start_title(self, attrsD):
        if self.svgOK:
            return self.unknown_starttag('title', attrsD.items())
        self.pushContent('title', attrsD, u'text/plain', self.infeed or self.inentry or self.insource)

    _start_dc_title = _start_title
    _start_media_title = _start_title

    def _end_title(self):
        if self.svgOK:
            return
        value = self.popContent('title')
        if not value:
            return
        self.title_depth = self.depth

    _end_dc_title = _end_title

    def _end_media_title(self):
        title_depth = self.title_depth
        self._end_title()
        self.title_depth = title_depth

    def _start_description(self, attrsD):
        context = self._getContext()
        if 'summary' in context:
            self._summaryKey = 'content'
            self._start_content(attrsD)
        else:
            self.pushContent('description', attrsD, u'text/html', self.infeed or self.inentry or self.insource)

    _start_dc_description = _start_description

    def _start_abstract(self, attrsD):
        self.pushContent('description', attrsD, u'text/plain', self.infeed or self.inentry or self.insource)

    def _end_description(self):
        if self._summaryKey == 'content':
            self._end_content()
        else:
            value = self.popContent('description')
        self._summaryKey = None
        return

    _end_abstract = _end_description
    _end_dc_description = _end_description

    def _start_info(self, attrsD):
        self.pushContent('info', attrsD, u'text/plain', 1)

    _start_feedburner_browserfriendly = _start_info

    def _end_info(self):
        self.popContent('info')

    _end_feedburner_browserfriendly = _end_info

    def _start_generator(self, attrsD):
        if attrsD:
            attrsD = self._itsAnHrefDamnIt(attrsD)
            if 'href' in attrsD:
                attrsD['href'] = self.resolveURI(attrsD['href'])
        self._getContext()['generator_detail'] = FeedParserDict(attrsD)
        self.push('generator', 1)

    def _end_generator(self):
        value = self.pop('generator')
        context = self._getContext()
        if 'generator_detail' in context:
            context['generator_detail']['name'] = value

    def _start_admin_generatoragent(self, attrsD):
        self.push('generator', 1)
        value = self._getAttribute(attrsD, 'rdf:resource')
        if value:
            self.elementstack[-1][2].append(value)
        self.pop('generator')
        self._getContext()['generator_detail'] = FeedParserDict({'href': value})

    def _start_admin_errorreportsto(self, attrsD):
        self.push('errorreportsto', 1)
        value = self._getAttribute(attrsD, 'rdf:resource')
        if value:
            self.elementstack[-1][2].append(value)
        self.pop('errorreportsto')

    def _start_summary(self, attrsD):
        context = self._getContext()
        if 'summary' in context:
            self._summaryKey = 'content'
            self._start_content(attrsD)
        else:
            self._summaryKey = 'summary'
            self.pushContent(self._summaryKey, attrsD, u'text/plain', 1)

    _start_itunes_summary = _start_summary

    def _end_summary(self):
        if self._summaryKey == 'content':
            self._end_content()
        else:
            self.popContent(self._summaryKey or 'summary')
        self._summaryKey = None
        return

    _end_itunes_summary = _end_summary

    def _start_enclosure(self, attrsD):
        attrsD = self._itsAnHrefDamnIt(attrsD)
        context = self._getContext()
        attrsD['rel'] = u'enclosure'
        context.setdefault('links', []).append(FeedParserDict(attrsD))

    def _start_source(self, attrsD):
        if 'url' in attrsD:
            self.sourcedata['href'] = attrsD[u'url']
        self.push('source', 1)
        self.insource = 1
        self.title_depth = -1

    def _end_source(self):
        self.insource = 0
        value = self.pop('source')
        if value:
            self.sourcedata['title'] = value
        self._getContext()['source'] = copy.deepcopy(self.sourcedata)
        self.sourcedata.clear()

    def _start_content(self, attrsD):
        self.pushContent('content', attrsD, u'text/plain', 1)
        src = attrsD.get('src')
        if src:
            self.contentparams['src'] = src
        self.push('content', 1)

    def _start_body(self, attrsD):
        self.pushContent('content', attrsD, u'application/xhtml+xml', 1)

    _start_xhtml_body = _start_body

    def _start_content_encoded(self, attrsD):
        self.pushContent('content', attrsD, u'text/html', 1)

    _start_fullitem = _start_content_encoded

    def _end_content(self):
        copyToSummary = self.mapContentType(self.contentparams.get('type')) in [u'text/plain'] + self.html_types
        value = self.popContent('content')
        if copyToSummary:
            self._save('summary', value)

    _end_body = _end_content
    _end_xhtml_body = _end_content
    _end_content_encoded = _end_content
    _end_fullitem = _end_content

    def _start_itunes_image(self, attrsD):
        self.push('itunes_image', 0)
        if attrsD.get('href'):
            self._getContext()['image'] = FeedParserDict({'href': attrsD.get('href')})
        elif attrsD.get('url'):
            self._getContext()['image'] = FeedParserDict({'href': attrsD.get('url')})

    _start_itunes_link = _start_itunes_image

    def _end_itunes_block(self):
        value = self.pop('itunes_block', 0)
        self._getContext()['itunes_block'] = value == 'yes' and 1 or 0

    def _end_itunes_explicit(self):
        value = self.pop('itunes_explicit', 0)
        self._getContext()['itunes_explicit'] = (None, False, True)[value == 'yes' and 2 or value == 'clean' or 0]
        return

    def _start_media_content(self, attrsD):
        context = self._getContext()
        context.setdefault('media_content', [])
        context['media_content'].append(attrsD)

    def _start_media_thumbnail(self, attrsD):
        context = self._getContext()
        context.setdefault('media_thumbnail', [])
        self.push('url', 1)
        context['media_thumbnail'].append(attrsD)

    def _end_media_thumbnail(self):
        url = self.pop('url')
        context = self._getContext()
        if url != None and len(url.strip()) != 0:
            if 'url' not in context['media_thumbnail'][-1]:
                context['media_thumbnail'][-1]['url'] = url
        return

    def _start_media_player(self, attrsD):
        self.push('media_player', 0)
        self._getContext()['media_player'] = FeedParserDict(attrsD)

    def _end_media_player(self):
        value = self.pop('media_player')
        context = self._getContext()
        context['media_player']['content'] = value

    def _start_newlocation(self, attrsD):
        self.push('newlocation', 1)

    def _end_newlocation(self):
        url = self.pop('newlocation')
        context = self._getContext()
        if context is not self.feeddata:
            return
        context['newlocation'] = _makeSafeAbsoluteURI(self.baseuri, url.strip())


if _XML_AVAILABLE:

    class _StrictFeedParser(_FeedParserMixin, xml.sax.handler.ContentHandler):

        def __init__(self, baseuri, baselang, encoding):
            xml.sax.handler.ContentHandler.__init__(self)
            _FeedParserMixin.__init__(self, baseuri, baselang, encoding)
            self.bozo = 0
            self.exc = None
            self.decls = {}
            return

        def startPrefixMapping(self, prefix, uri):
            if not uri:
                return
            else:
                prefix = prefix or None
                self.trackNamespace(prefix, uri)
                if prefix and uri == 'http://www.w3.org/1999/xlink':
                    self.decls['xmlns:' + prefix] = uri
                return

        def startElementNS(self, name, qname, attrs):
            namespace, localname = name
            lowernamespace = str(namespace or '').lower()
            if lowernamespace.find(u'backend.userland.com/rss') != -1:
                namespace = u'http://backend.userland.com/rss'
                lowernamespace = namespace
            if qname and qname.find(':') > 0:
                givenprefix = qname.split(':')[0]
            else:
                givenprefix = None
            prefix = self._matchnamespaces.get(lowernamespace, givenprefix)
            if givenprefix and (prefix == None or prefix == '' and lowernamespace == '') and givenprefix not in self.namespacesInUse:
                raise UndeclaredNamespace, "'%s' is not associated with a namespace" % givenprefix
            localname = str(localname).lower()
            attrsD, self.decls = self.decls, {}
            if localname == 'math' and namespace == 'http://www.w3.org/1998/Math/MathML':
                attrsD['xmlns'] = namespace
            if localname == 'svg' and namespace == 'http://www.w3.org/2000/svg':
                attrsD['xmlns'] = namespace
            if prefix:
                localname = prefix.lower() + ':' + localname
            elif namespace and not qname:
                for name, value in self.namespacesInUse.items():
                    if name and value == namespace:
                        localname = name + ':' + localname
                        break

            for (namespace, attrlocalname), attrvalue in attrs.items():
                lowernamespace = (namespace or '').lower()
                prefix = self._matchnamespaces.get(lowernamespace, '')
                if prefix:
                    attrlocalname = prefix + ':' + attrlocalname
                attrsD[str(attrlocalname).lower()] = attrvalue

            for qname in attrs.getQNames():
                attrsD[str(qname).lower()] = attrs.getValueByQName(qname)

            self.unknown_starttag(localname, attrsD.items())
            return

        def characters(self, text):
            self.handle_data(text)

        def endElementNS(self, name, qname):
            namespace, localname = name
            lowernamespace = str(namespace or '').lower()
            if qname and qname.find(':') > 0:
                givenprefix = qname.split(':')[0]
            else:
                givenprefix = ''
            prefix = self._matchnamespaces.get(lowernamespace, givenprefix)
            if prefix:
                localname = prefix + ':' + localname
            elif namespace and not qname:
                for name, value in self.namespacesInUse.items():
                    if name and value == namespace:
                        localname = name + ':' + localname
                        break

            localname = str(localname).lower()
            self.unknown_endtag(localname)

        def error(self, exc):
            self.bozo = 1
            self.exc = exc

        warning = error

        def fatalError(self, exc):
            self.error(exc)
            raise exc


class _BaseHTMLProcessor(sgmllib.SGMLParser):
    special = re.compile('[<>\'"]')
    bare_ampersand = re.compile('&(?!#\\d+;|#x[0-9a-fA-F]+;|\\w+;)')
    elements_no_end_tag = set(['area',
     'base',
     'basefont',
     'br',
     'col',
     'command',
     'embed',
     'frame',
     'hr',
     'img',
     'input',
     'isindex',
     'keygen',
     'link',
     'meta',
     'param',
     'source',
     'track',
     'wbr'])

    def __init__(self, encoding, _type):
        self.encoding = encoding
        self._type = _type
        sgmllib.SGMLParser.__init__(self)

    def reset(self):
        self.pieces = []
        sgmllib.SGMLParser.reset(self)

    def _shorttag_replace(self, match):
        tag = match.group(1)
        if tag in self.elements_no_end_tag:
            return '<' + tag + ' />'
        else:
            return '<' + tag + '></' + tag + '>'

    def goahead(self, i):
        pass

    goahead.func_code = sgmllib.SGMLParser.goahead.func_code

    def __parse_starttag(self, i):
        pass

    __parse_starttag.func_code = sgmllib.SGMLParser.parse_starttag.func_code

    def parse_starttag(self, i):
        j = self.__parse_starttag(i)
        if self._type == 'application/xhtml+xml':
            if j > 2 and self.rawdata[j - 2:j] == '/>':
                self.unknown_endtag(self.lasttag)
        return j

    def feed(self, data):
        data = re.compile('<!((?!DOCTYPE|--|\\[))', re.IGNORECASE).sub('&lt;!\\1', data)
        data = re.sub('<([^<>\\s]+?)\\s*/>', self._shorttag_replace, data)
        data = data.replace('&#39;', "'")
        data = data.replace('&#34;', '"')
        try:
            bytes
            if bytes is str:
                raise NameError
            self.encoding = self.encoding + u'_INVALID_PYTHON_3'
        except NameError:
            if self.encoding and isinstance(data, unicode):
                data = data.encode(self.encoding)

        sgmllib.SGMLParser.feed(self, data)
        sgmllib.SGMLParser.close(self)

    def normalize_attrs(self, attrs):
        if not attrs:
            return attrs
        attrs = dict([ (k.lower(), v) for k, v in attrs ]).items()
        attrs = [ (k, k in ('rel', 'type') and v.lower() or v) for k, v in attrs ]
        attrs.sort()
        return attrs

    def unknown_starttag(self, tag, attrs):
        uattrs = []
        strattrs = ''
        if attrs:
            for key, value in attrs:
                value = value.replace('>', '&gt;').replace('<', '&lt;').replace('"', '&quot;')
                value = self.bare_ampersand.sub('&amp;', value)
                if not isinstance(value, unicode):
                    value = value.decode(self.encoding, 'ignore')
                try:
                    uattrs.append((unicode(key, self.encoding), value))
                except TypeError:
                    uattrs.append((key, value))

            strattrs = u''.join([ u' %s="%s"' % (key, value) for key, value in uattrs ])
            if self.encoding:
                try:
                    strattrs = strattrs.encode(self.encoding)
                except (UnicodeEncodeError, LookupError):
                    pass

        if tag in self.elements_no_end_tag:
            self.pieces.append('<%s%s />' % (tag, strattrs))
        else:
            self.pieces.append('<%s%s>' % (tag, strattrs))

    def unknown_endtag(self, tag):
        if tag not in self.elements_no_end_tag:
            self.pieces.append('</%s>' % tag)

    def handle_charref(self, ref):
        if ref.startswith('x'):
            value = int(ref[1:], 16)
        else:
            value = int(ref)
        if value in _cp1252:
            self.pieces.append('&#%s;' % hex(ord(_cp1252[value]))[1:])
        else:
            self.pieces.append('&#%s;' % ref)

    def handle_entityref(self, ref):
        if ref in name2codepoint or ref == 'apos':
            self.pieces.append('&%s;' % ref)
        else:
            self.pieces.append('&amp;%s' % ref)

    def handle_data(self, text):
        self.pieces.append(text)

    def handle_comment(self, text):
        self.pieces.append('<!--%s-->' % text)

    def handle_pi(self, text):
        self.pieces.append('<?%s>' % text)

    def handle_decl(self, text):
        self.pieces.append('<!%s>' % text)

    _new_declname_match = re.compile('[a-zA-Z][-_.a-zA-Z0-9:]*\\s*').match

    def _scan_name(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        if i == n:
            return (None, -1)
        else:
            m = self._new_declname_match(rawdata, i)
            if m:
                s = m.group()
                name = s.strip()
                if i + len(s) == n:
                    return (None, -1)
                return (name.lower(), m.end())
            self.handle_data(rawdata)
            return (None, -1)
            return None

    def convert_charref(self, name):
        return '&#%s;' % name

    def convert_entityref(self, name):
        return '&%s;' % name

    def output(self):
        """Return processed HTML as a single string"""
        return ''.join([ str(p) for p in self.pieces ])

    def parse_declaration(self, i):
        try:
            return sgmllib.SGMLParser.parse_declaration(self, i)
        except sgmllib.SGMLParseError:
            self.handle_data('&lt;')
            return i + 1


class _LooseFeedParser(_FeedParserMixin, _BaseHTMLProcessor):

    def __init__(self, baseuri, baselang, encoding, entities):
        sgmllib.SGMLParser.__init__(self)
        _FeedParserMixin.__init__(self, baseuri, baselang, encoding)
        _BaseHTMLProcessor.__init__(self, encoding, 'application/xhtml+xml')
        self.entities = entities

    def decodeEntities(self, element, data):
        data = data.replace('&#60;', '&lt;')
        data = data.replace('&#x3c;', '&lt;')
        data = data.replace('&#x3C;', '&lt;')
        data = data.replace('&#62;', '&gt;')
        data = data.replace('&#x3e;', '&gt;')
        data = data.replace('&#x3E;', '&gt;')
        data = data.replace('&#38;', '&amp;')
        data = data.replace('&#x26;', '&amp;')
        data = data.replace('&#34;', '&quot;')
        data = data.replace('&#x22;', '&quot;')
        data = data.replace('&#39;', '&apos;')
        data = data.replace('&#x27;', '&apos;')
        if not self.contentparams.get('type', u'xml').endswith(u'xml'):
            data = data.replace('&lt;', '<')
            data = data.replace('&gt;', '>')
            data = data.replace('&amp;', '&')
            data = data.replace('&quot;', '"')
            data = data.replace('&apos;', "'")
        return data

    def strattrs(self, attrs):
        return ''.join([ ' %s="%s"' % (n, v.replace('"', '&quot;')) for n, v in attrs ])


class _MicroformatsParser():
    STRING = 1
    DATE = 2
    URI = 3
    NODE = 4
    EMAIL = 5
    known_xfn_relationships = set(['contact',
     'acquaintance',
     'friend',
     'met',
     'co-worker',
     'coworker',
     'colleague',
     'co-resident',
     'coresident',
     'neighbor',
     'child',
     'parent',
     'sibling',
     'brother',
     'sister',
     'spouse',
     'wife',
     'husband',
     'kin',
     'relative',
     'muse',
     'crush',
     'date',
     'sweetheart',
     'me'])
    known_binary_extensions = set(['zip',
     'rar',
     'exe',
     'gz',
     'tar',
     'tgz',
     'tbz2',
     'bz2',
     'z',
     '7z',
     'dmg',
     'img',
     'sit',
     'sitx',
     'hqx',
     'deb',
     'rpm',
     'bz2',
     'jar',
     'rar',
     'iso',
     'bin',
     'msi',
     'mp2',
     'mp3',
     'ogg',
     'ogm',
     'mp4',
     'm4v',
     'm4a',
     'avi',
     'wma',
     'wmv'])

    def __init__(self, data, baseuri, encoding):
        self.document = BeautifulSoup.BeautifulSoup(data)
        self.baseuri = baseuri
        self.encoding = encoding
        if isinstance(data, unicode):
            data = data.encode(encoding)
        self.tags = []
        self.enclosures = []
        self.xfn = []
        self.vcard = None
        return

    def vcardEscape(self, s):
        if isinstance(s, basestring):
            s = s.replace(',', '\\,').replace(';', '\\;').replace('\n', '\\n')
        return s

    def vcardFold(self, s):
        s = re.sub(';+$', '', s)
        sFolded = ''
        iMax = 75
        sPrefix = ''
        while len(s) > iMax:
            sFolded += sPrefix + s[:iMax] + '\n'
            s = s[iMax:]
            sPrefix = ' '
            iMax = 74

        sFolded += sPrefix + s
        return sFolded

    def normalize(self, s):
        return re.sub('\\s+', ' ', s).strip()

    def unique(self, aList):
        results = []
        for element in aList:
            if element not in results:
                results.append(element)

        return results

    def toISO8601(self, dt):
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', dt)

    def getPropertyValue(self, elmRoot, sProperty, iPropertyType = 4, bAllowMultiple = 0, bAutoEscape = 0):
        all = lambda x: 1
        sProperty = sProperty.lower()
        bFound = 0
        bNormalize = 1
        propertyMatch = {'class': re.compile('\\b%s\\b' % sProperty)}
        if bAllowMultiple and iPropertyType != self.NODE:
            snapResults = []
            containers = elmRoot(['ul', 'ol'], propertyMatch)
            for container in containers:
                snapResults.extend(container('li'))

            bFound = len(snapResults) != 0
        if not bFound:
            snapResults = elmRoot(all, propertyMatch)
            bFound = len(snapResults) != 0
        if not bFound and sProperty == 'value':
            snapResults = elmRoot('pre')
            bFound = len(snapResults) != 0
            bNormalize = not bFound
            if not bFound:
                snapResults = [elmRoot]
                bFound = len(snapResults) != 0
        arFilter = []
        if sProperty == 'vcard':
            snapFilter = elmRoot(all, propertyMatch)
            for node in snapFilter:
                if node.findParent(all, propertyMatch):
                    arFilter.append(node)

        arResults = []
        for node in snapResults:
            if node not in arFilter:
                arResults.append(node)

        bFound = len(arResults) != 0
        if not bFound:
            if bAllowMultiple:
                return []
            elif iPropertyType == self.STRING:
                return ''
            elif iPropertyType == self.DATE:
                return
            elif iPropertyType == self.URI:
                return ''
            elif iPropertyType == self.NODE:
                return
            else:
                return
        arValues = []
        for elmResult in arResults:
            sValue = None
            if iPropertyType == self.NODE:
                if bAllowMultiple:
                    arValues.append(elmResult)
                    continue
                else:
                    return elmResult
            sNodeName = elmResult.name.lower()
            if iPropertyType == self.EMAIL and sNodeName == 'a':
                sValue = (elmResult.get('href') or '').split('mailto:').pop().split('?')[0]
            if sValue:
                sValue = bNormalize and self.normalize(sValue) or sValue.strip()
            if not sValue and sNodeName == 'abbr':
                sValue = elmResult.get('title')
            if sValue:
                sValue = bNormalize and self.normalize(sValue) or sValue.strip()
            if not sValue and iPropertyType == self.URI:
                if sNodeName == 'a':
                    sValue = elmResult.get('href')
                elif sNodeName == 'img':
                    sValue = elmResult.get('src')
                elif sNodeName == 'object':
                    sValue = elmResult.get('data')
            if sValue:
                sValue = bNormalize and self.normalize(sValue) or sValue.strip()
            if not sValue and sNodeName == 'img':
                sValue = elmResult.get('alt')
            if sValue:
                sValue = bNormalize and self.normalize(sValue) or sValue.strip()
            if not sValue:
                sValue = elmResult.renderContents()
                sValue = re.sub('<\\S[^>]*>', '', sValue)
                sValue = sValue.replace('\r\n', '\n')
                sValue = sValue.replace('\r', '\n')
            if sValue:
                sValue = bNormalize and self.normalize(sValue) or sValue.strip()
            if not sValue:
                continue
            if iPropertyType == self.DATE:
                sValue = _parse_date_iso8601(sValue)
            if bAllowMultiple:
                arValues.append(bAutoEscape and self.vcardEscape(sValue) or sValue)
            else:
                return bAutoEscape and self.vcardEscape(sValue) or sValue

        return arValues

    def findVCards(self, elmRoot, bAgentParsing = 0):
        sVCards = ''
        if not bAgentParsing:
            arCards = self.getPropertyValue(elmRoot, 'vcard', bAllowMultiple=1)
        else:
            arCards = [elmRoot]
        for elmCard in arCards:
            arLines = []

            def processSingleString(sProperty):
                sValue = self.getPropertyValue(elmCard, sProperty, self.STRING, bAutoEscape=1).decode(self.encoding)
                if sValue:
                    arLines.append(self.vcardFold(sProperty.upper() + ':' + sValue))
                return sValue or u''

            def processSingleURI(sProperty):
                sValue = self.getPropertyValue(elmCard, sProperty, self.URI)
                if sValue:
                    sContentType = ''
                    sEncoding = ''
                    sValueKey = ''
                    if sValue.startswith('data:'):
                        sEncoding = ';ENCODING=b'
                        sContentType = sValue.split(';')[0].split('/').pop()
                        sValue = sValue.split(',', 1).pop()
                    else:
                        elmValue = self.getPropertyValue(elmCard, sProperty)
                        if elmValue:
                            if sProperty != 'url':
                                sValueKey = ';VALUE=uri'
                            sContentType = elmValue.get('type', '').strip().split('/').pop().strip()
                    sContentType = sContentType.upper()
                    if sContentType == 'OCTET-STREAM':
                        sContentType = ''
                    if sContentType:
                        sContentType = ';TYPE=' + sContentType.upper()
                    arLines.append(self.vcardFold(sProperty.upper() + sEncoding + sContentType + sValueKey + ':' + sValue))

            def processTypeValue(sProperty, arDefaultType, arForceType = None):
                arResults = self.getPropertyValue(elmCard, sProperty, bAllowMultiple=1)
                for elmResult in arResults:
                    arType = self.getPropertyValue(elmResult, 'type', self.STRING, 1, 1)
                    if arForceType:
                        arType = self.unique(arForceType + arType)
                    if not arType:
                        arType = arDefaultType
                    sValue = self.getPropertyValue(elmResult, 'value', self.EMAIL, 0)
                    if sValue:
                        arLines.append(self.vcardFold(sProperty.upper() + ';TYPE=' + ','.join(arType) + ':' + sValue))

            arAgent = self.getPropertyValue(elmCard, 'agent', bAllowMultiple=1)
            for elmAgent in arAgent:
                if re.compile('\\bvcard\\b').search(elmAgent.get('class')):
                    sAgentValue = self.findVCards(elmAgent, 1) + '\n'
                    sAgentValue = sAgentValue.replace('\n', '\\n')
                    sAgentValue = sAgentValue.replace(';', '\\;')
                    if sAgentValue:
                        arLines.append(self.vcardFold('AGENT:' + sAgentValue))
                    elmAgent.extract()
                else:
                    sAgentValue = self.getPropertyValue(elmAgent, 'value', self.URI, bAutoEscape=1)
                    if sAgentValue:
                        arLines.append(self.vcardFold('AGENT;VALUE=uri:' + sAgentValue))

            sFN = processSingleString('fn')
            elmName = self.getPropertyValue(elmCard, 'n')
            if elmName:
                sFamilyName = self.getPropertyValue(elmName, 'family-name', self.STRING, bAutoEscape=1)
                sGivenName = self.getPropertyValue(elmName, 'given-name', self.STRING, bAutoEscape=1)
                arAdditionalNames = self.getPropertyValue(elmName, 'additional-name', self.STRING, 1, 1) + self.getPropertyValue(elmName, 'additional-names', self.STRING, 1, 1)
                arHonorificPrefixes = self.getPropertyValue(elmName, 'honorific-prefix', self.STRING, 1, 1) + self.getPropertyValue(elmName, 'honorific-prefixes', self.STRING, 1, 1)
                arHonorificSuffixes = self.getPropertyValue(elmName, 'honorific-suffix', self.STRING, 1, 1) + self.getPropertyValue(elmName, 'honorific-suffixes', self.STRING, 1, 1)
                arLines.append(self.vcardFold('N:' + sFamilyName + ';' + sGivenName + ';' + ','.join(arAdditionalNames) + ';' + ','.join(arHonorificPrefixes) + ';' + ','.join(arHonorificSuffixes)))
            elif sFN:
                arNames = self.normalize(sFN).split()
                if len(arNames) == 2:
                    bFamilyNameFirst = arNames[0].endswith(',') or len(arNames[1]) == 1 or len(arNames[1]) == 2 and arNames[1].endswith('.')
                    if bFamilyNameFirst:
                        arLines.append(self.vcardFold('N:' + arNames[0] + ';' + arNames[1]))
                    else:
                        arLines.append(self.vcardFold('N:' + arNames[1] + ';' + arNames[0]))
            sSortString = self.getPropertyValue(elmCard, 'sort-string', self.STRING, bAutoEscape=1)
            if sSortString:
                arLines.append(self.vcardFold('SORT-STRING:' + sSortString))
            arNickname = self.getPropertyValue(elmCard, 'nickname', self.STRING, 1, 1)
            if arNickname:
                arLines.append(self.vcardFold('NICKNAME:' + ','.join(arNickname)))
            processSingleURI('photo')
            dtBday = self.getPropertyValue(elmCard, 'bday', self.DATE)
            if dtBday:
                arLines.append(self.vcardFold('BDAY:' + self.toISO8601(dtBday)))
            arAdr = self.getPropertyValue(elmCard, 'adr', bAllowMultiple=1)
            for elmAdr in arAdr:
                arType = self.getPropertyValue(elmAdr, 'type', self.STRING, 1, 1)
                if not arType:
                    arType = ['intl',
                     'postal',
                     'parcel',
                     'work']
                sPostOfficeBox = self.getPropertyValue(elmAdr, 'post-office-box', self.STRING, 0, 1)
                sExtendedAddress = self.getPropertyValue(elmAdr, 'extended-address', self.STRING, 0, 1)
                sStreetAddress = self.getPropertyValue(elmAdr, 'street-address', self.STRING, 0, 1)
                sLocality = self.getPropertyValue(elmAdr, 'locality', self.STRING, 0, 1)
                sRegion = self.getPropertyValue(elmAdr, 'region', self.STRING, 0, 1)
                sPostalCode = self.getPropertyValue(elmAdr, 'postal-code', self.STRING, 0, 1)
                sCountryName = self.getPropertyValue(elmAdr, 'country-name', self.STRING, 0, 1)
                arLines.append(self.vcardFold('ADR;TYPE=' + ','.join(arType) + ':' + sPostOfficeBox + ';' + sExtendedAddress + ';' + sStreetAddress + ';' + sLocality + ';' + sRegion + ';' + sPostalCode + ';' + sCountryName))

            processTypeValue('label', ['intl',
             'postal',
             'parcel',
             'work'])
            processTypeValue('tel', ['voice'])
            processTypeValue('email', ['internet'], ['internet'])
            processSingleString('mailer')
            processSingleString('tz')
            elmGeo = self.getPropertyValue(elmCard, 'geo')
            if elmGeo:
                sLatitude = self.getPropertyValue(elmGeo, 'latitude', self.STRING, 0, 1)
                sLongitude = self.getPropertyValue(elmGeo, 'longitude', self.STRING, 0, 1)
                arLines.append(self.vcardFold('GEO:' + sLatitude + ';' + sLongitude))
            processSingleString('title')
            processSingleString('role')
            processSingleURI('logo')
            elmOrg = self.getPropertyValue(elmCard, 'org')
            if elmOrg:
                sOrganizationName = self.getPropertyValue(elmOrg, 'organization-name', self.STRING, 0, 1)
                if not sOrganizationName:
                    sOrganizationName = self.getPropertyValue(elmCard, 'org', self.STRING, 0, 1)
                    if sOrganizationName:
                        arLines.append(self.vcardFold('ORG:' + sOrganizationName))
                else:
                    arOrganizationUnit = self.getPropertyValue(elmOrg, 'organization-unit', self.STRING, 1, 1)
                    arLines.append(self.vcardFold('ORG:' + sOrganizationName + ';' + ';'.join(arOrganizationUnit)))
            arCategory = self.getPropertyValue(elmCard, 'category', self.STRING, 1, 1) + self.getPropertyValue(elmCard, 'categories', self.STRING, 1, 1)
            if arCategory:
                arLines.append(self.vcardFold('CATEGORIES:' + ','.join(arCategory)))
            processSingleString('note')
            processSingleString('rev')
            processSingleURI('sound')
            processSingleString('uid')
            processSingleURI('url')
            processSingleString('class')
            processSingleURI('key')
            if arLines:
                arLines = [u'BEGIN:vCard', u'VERSION:3.0'] + arLines + [u'END:vCard']
                for i, s in enumerate(arLines):
                    if not isinstance(s, unicode):
                        arLines[i] = s.decode('utf-8', 'ignore')

                sVCards += u'\n'.join(arLines) + u'\n'

        return sVCards.strip()

    def isProbablyDownloadable(self, elm):
        attrsD = elm.attrMap
        if 'href' not in attrsD:
            return 0
        linktype = attrsD.get('type', '').strip()
        if linktype.startswith('audio/') or linktype.startswith('video/') or linktype.startswith('application/') and not linktype.endswith('xml'):
            return 1
        path = urlparse.urlparse(attrsD['href'])[2]
        if path.find('.') == -1:
            return 0
        fileext = path.split('.').pop().lower()
        return fileext in self.known_binary_extensions

    def findTags(self):
        all = lambda x: 1
        for elm in self.document(all, {'rel': re.compile('\\btag\\b')}):
            href = elm.get('href')
            if not href:
                continue
            urlscheme, domain, path, params, query, fragment = urlparse.urlparse(_urljoin(self.baseuri, href))
            segments = path.split('/')
            tag = segments.pop()
            if not tag:
                if segments:
                    tag = segments.pop()
                else:
                    continue
            tagscheme = urlparse.urlunparse((urlscheme,
             domain,
             '/'.join(segments),
             '',
             '',
             ''))
            if not tagscheme.endswith('/'):
                tagscheme += '/'
            self.tags.append(FeedParserDict({'term': tag,
             'scheme': tagscheme,
             'label': elm.string or ''}))

    def findEnclosures(self):
        all = lambda x: 1
        enclosure_match = re.compile('\\benclosure\\b')
        for elm in self.document(all, {'href': re.compile('.+')}):
            if not enclosure_match.search(elm.get('rel', u'')) and not self.isProbablyDownloadable(elm):
                continue
            if elm.attrMap not in self.enclosures:
                self.enclosures.append(elm.attrMap)
                if elm.string and not elm.get('title'):
                    self.enclosures[-1]['title'] = elm.string

    def findXFN(self):
        all = lambda x: 1
        for elm in self.document(all, {'rel': re.compile('.+'),
         'href': re.compile('.+')}):
            rels = elm.get('rel', u'').split()
            xfn_rels = [ r for r in rels if r in self.known_xfn_relationships ]
            if xfn_rels:
                self.xfn.append({'relationships': xfn_rels,
                 'href': elm.get('href', ''),
                 'name': elm.string})


def _parseMicroformats(htmlSource, baseURI, encoding):
    if not BeautifulSoup:
        return
    try:
        p = _MicroformatsParser(htmlSource, baseURI, encoding)
    except UnicodeEncodeError:
        return

    p.vcard = p.findVCards(p.document)
    p.findTags()
    p.findEnclosures()
    p.findXFN()
    return {'tags': p.tags,
     'enclosures': p.enclosures,
     'xfn': p.xfn,
     'vcard': p.vcard}


class _RelativeURIResolver(_BaseHTMLProcessor):
    relative_uris = set([('a', 'href'),
     ('applet', 'codebase'),
     ('area', 'href'),
     ('blockquote', 'cite'),
     ('body', 'background'),
     ('del', 'cite'),
     ('form', 'action'),
     ('frame', 'longdesc'),
     ('frame', 'src'),
     ('iframe', 'longdesc'),
     ('iframe', 'src'),
     ('head', 'profile'),
     ('img', 'longdesc'),
     ('img', 'src'),
     ('img', 'usemap'),
     ('input', 'src'),
     ('input', 'usemap'),
     ('ins', 'cite'),
     ('link', 'href'),
     ('object', 'classid'),
     ('object', 'codebase'),
     ('object', 'data'),
     ('object', 'usemap'),
     ('q', 'cite'),
     ('script', 'src')])

    def __init__(self, baseuri, encoding, _type):
        _BaseHTMLProcessor.__init__(self, encoding, _type)
        self.baseuri = baseuri

    def resolveURI(self, uri):
        return _makeSafeAbsoluteURI(self.baseuri, uri.strip())

    def unknown_starttag(self, tag, attrs):
        attrs = self.normalize_attrs(attrs)
        attrs = [ (key, (tag, key) in self.relative_uris and self.resolveURI(value) or value) for key, value in attrs ]
        _BaseHTMLProcessor.unknown_starttag(self, tag, attrs)


def _resolveRelativeURIs(htmlSource, baseURI, encoding, _type):
    if not _SGML_AVAILABLE:
        return htmlSource
    p = _RelativeURIResolver(baseURI, encoding, _type)
    p.feed(htmlSource)
    return p.output()


def _makeSafeAbsoluteURI(base, rel = None):
    if not ACCEPTABLE_URI_SCHEMES:
        try:
            return _urljoin(base, rel or u'')
        except ValueError:
            return u''

    if not base:
        return rel or u''
    if not rel:
        try:
            scheme = urlparse.urlparse(base)[0]
        except ValueError:
            return u''

        if not scheme or scheme in ACCEPTABLE_URI_SCHEMES:
            return base
        return u''
    try:
        uri = _urljoin(base, rel)
    except ValueError:
        return u''

    if uri.strip().split(':', 1)[0] not in ACCEPTABLE_URI_SCHEMES:
        return u''
    return uri


class _HTMLSanitizer(_BaseHTMLProcessor):
    acceptable_elements = set(['a',
     'abbr',
     'acronym',
     'address',
     'area',
     'article',
     'aside',
     'audio',
     'b',
     'big',
     'blockquote',
     'br',
     'button',
     'canvas',
     'caption',
     'center',
     'cite',
     'code',
     'col',
     'colgroup',
     'command',
     'datagrid',
     'datalist',
     'dd',
     'del',
     'details',
     'dfn',
     'dialog',
     'dir',
     'div',
     'dl',
     'dt',
     'em',
     'event-source',
     'fieldset',
     'figcaption',
     'figure',
     'footer',
     'font',
     'form',
     'header',
     'h1',
     'h2',
     'h3',
     'h4',
     'h5',
     'h6',
     'hr',
     'i',
     'img',
     'input',
     'ins',
     'keygen',
     'kbd',
     'label',
     'legend',
     'li',
     'm',
     'map',
     'menu',
     'meter',
     'multicol',
     'nav',
     'nextid',
     'ol',
     'output',
     'optgroup',
     'option',
     'p',
     'pre',
     'progress',
     'q',
     's',
     'samp',
     'section',
     'select',
     'small',
     'sound',
     'source',
     'spacer',
     'span',
     'strike',
     'strong',
     'sub',
     'sup',
     'table',
     'tbody',
     'td',
     'textarea',
     'time',
     'tfoot',
     'th',
     'thead',
     'tr',
     'tt',
     'u',
     'ul',
     'var',
     'video',
     'noscript'])
    acceptable_attributes = set(['abbr',
     'accept',
     'accept-charset',
     'accesskey',
     'action',
     'align',
     'alt',
     'autocomplete',
     'autofocus',
     'axis',
     'background',
     'balance',
     'bgcolor',
     'bgproperties',
     'border',
     'bordercolor',
     'bordercolordark',
     'bordercolorlight',
     'bottompadding',
     'cellpadding',
     'cellspacing',
     'ch',
     'challenge',
     'char',
     'charoff',
     'choff',
     'charset',
     'checked',
     'cite',
     'class',
     'clear',
     'color',
     'cols',
     'colspan',
     'compact',
     'contenteditable',
     'controls',
     'coords',
     'data',
     'datafld',
     'datapagesize',
     'datasrc',
     'datetime',
     'default',
     'delay',
     'dir',
     'disabled',
     'draggable',
     'dynsrc',
     'enctype',
     'end',
     'face',
     'for',
     'form',
     'frame',
     'galleryimg',
     'gutter',
     'headers',
     'height',
     'hidefocus',
     'hidden',
     'high',
     'href',
     'hreflang',
     'hspace',
     'icon',
     'id',
     'inputmode',
     'ismap',
     'keytype',
     'label',
     'leftspacing',
     'lang',
     'list',
     'longdesc',
     'loop',
     'loopcount',
     'loopend',
     'loopstart',
     'low',
     'lowsrc',
     'max',
     'maxlength',
     'media',
     'method',
     'min',
     'multiple',
     'name',
     'nohref',
     'noshade',
     'nowrap',
     'open',
     'optimum',
     'pattern',
     'ping',
     'point-size',
     'prompt',
     'pqg',
     'radiogroup',
     'readonly',
     'rel',
     'repeat-max',
     'repeat-min',
     'replace',
     'required',
     'rev',
     'rightspacing',
     'rows',
     'rowspan',
     'rules',
     'scope',
     'selected',
     'shape',
     'size',
     'span',
     'src',
     'start',
     'step',
     'summary',
     'suppress',
     'tabindex',
     'target',
     'template',
     'title',
     'toppadding',
     'type',
     'unselectable',
     'usemap',
     'urn',
     'valign',
     'value',
     'variable',
     'volume',
     'vspace',
     'vrml',
     'width',
     'wrap',
     'xml:lang'])
    unacceptable_elements_with_end_tag = set(['script', 'applet', 'style'])
    acceptable_css_properties = set(['azimuth',
     'background-color',
     'border-bottom-color',
     'border-collapse',
     'border-color',
     'border-left-color',
     'border-right-color',
     'border-top-color',
     'clear',
     'color',
     'cursor',
     'direction',
     'display',
     'elevation',
     'float',
     'font',
     'font-family',
     'font-size',
     'font-style',
     'font-variant',
     'font-weight',
     'height',
     'letter-spacing',
     'line-height',
     'overflow',
     'pause',
     'pause-after',
     'pause-before',
     'pitch',
     'pitch-range',
     'richness',
     'speak',
     'speak-header',
     'speak-numeral',
     'speak-punctuation',
     'speech-rate',
     'stress',
     'text-align',
     'text-decoration',
     'text-indent',
     'unicode-bidi',
     'vertical-align',
     'voice-family',
     'volume',
     'white-space',
     'width'])
    acceptable_css_keywords = set(['auto',
     'aqua',
     'black',
     'block',
     'blue',
     'bold',
     'both',
     'bottom',
     'brown',
     'center',
     'collapse',
     'dashed',
     'dotted',
     'fuchsia',
     'gray',
     'green',
     '!important',
     'italic',
     'left',
     'lime',
     'maroon',
     'medium',
     'none',
     'navy',
     'normal',
     'nowrap',
     'olive',
     'pointer',
     'purple',
     'red',
     'right',
     'solid',
     'silver',
     'teal',
     'top',
     'transparent',
     'underline',
     'white',
     'yellow'])
    valid_css_values = re.compile('^(#[0-9a-f]+|rgb\\(\\d+%?,\\d*%?,?\\d*%?\\)?|' + '\\d{0,2}\\.?\\d{0,2}(cm|em|ex|in|mm|pc|pt|px|%|,|\\))?)$')
    mathml_elements = set(['annotation',
     'annotation-xml',
     'maction',
     'math',
     'merror',
     'mfenced',
     'mfrac',
     'mi',
     'mmultiscripts',
     'mn',
     'mo',
     'mover',
     'mpadded',
     'mphantom',
     'mprescripts',
     'mroot',
     'mrow',
     'mspace',
     'msqrt',
     'mstyle',
     'msub',
     'msubsup',
     'msup',
     'mtable',
     'mtd',
     'mtext',
     'mtr',
     'munder',
     'munderover',
     'none',
     'semantics'])
    mathml_attributes = set(['actiontype',
     'align',
     'columnalign',
     'columnalign',
     'columnalign',
     'close',
     'columnlines',
     'columnspacing',
     'columnspan',
     'depth',
     'display',
     'displaystyle',
     'encoding',
     'equalcolumns',
     'equalrows',
     'fence',
     'fontstyle',
     'fontweight',
     'frame',
     'height',
     'linethickness',
     'lspace',
     'mathbackground',
     'mathcolor',
     'mathvariant',
     'mathvariant',
     'maxsize',
     'minsize',
     'open',
     'other',
     'rowalign',
     'rowalign',
     'rowalign',
     'rowlines',
     'rowspacing',
     'rowspan',
     'rspace',
     'scriptlevel',
     'selection',
     'separator',
     'separators',
     'stretchy',
     'width',
     'width',
     'xlink:href',
     'xlink:show',
     'xlink:type',
     'xmlns',
     'xmlns:xlink'])
    svg_elements = set(['a',
     'animate',
     'animateColor',
     'animateMotion',
     'animateTransform',
     'circle',
     'defs',
     'desc',
     'ellipse',
     'foreignObject',
     'font-face',
     'font-face-name',
     'font-face-src',
     'g',
     'glyph',
     'hkern',
     'linearGradient',
     'line',
     'marker',
     'metadata',
     'missing-glyph',
     'mpath',
     'path',
     'polygon',
     'polyline',
     'radialGradient',
     'rect',
     'set',
     'stop',
     'svg',
     'switch',
     'text',
     'title',
     'tspan',
     'use'])
    svg_attributes = set(['accent-height',
     'accumulate',
     'additive',
     'alphabetic',
     'arabic-form',
     'ascent',
     'attributeName',
     'attributeType',
     'baseProfile',
     'bbox',
     'begin',
     'by',
     'calcMode',
     'cap-height',
     'class',
     'color',
     'color-rendering',
     'content',
     'cx',
     'cy',
     'd',
     'dx',
     'dy',
     'descent',
     'display',
     'dur',
     'end',
     'fill',
     'fill-opacity',
     'fill-rule',
     'font-family',
     'font-size',
     'font-stretch',
     'font-style',
     'font-variant',
     'font-weight',
     'from',
     'fx',
     'fy',
     'g1',
     'g2',
     'glyph-name',
     'gradientUnits',
     'hanging',
     'height',
     'horiz-adv-x',
     'horiz-origin-x',
     'id',
     'ideographic',
     'k',
     'keyPoints',
     'keySplines',
     'keyTimes',
     'lang',
     'mathematical',
     'marker-end',
     'marker-mid',
     'marker-start',
     'markerHeight',
     'markerUnits',
     'markerWidth',
     'max',
     'min',
     'name',
     'offset',
     'opacity',
     'orient',
     'origin',
     'overline-position',
     'overline-thickness',
     'panose-1',
     'path',
     'pathLength',
     'points',
     'preserveAspectRatio',
     'r',
     'refX',
     'refY',
     'repeatCount',
     'repeatDur',
     'requiredExtensions',
     'requiredFeatures',
     'restart',
     'rotate',
     'rx',
     'ry',
     'slope',
     'stemh',
     'stemv',
     'stop-color',
     'stop-opacity',
     'strikethrough-position',
     'strikethrough-thickness',
     'stroke',
     'stroke-dasharray',
     'stroke-dashoffset',
     'stroke-linecap',
     'stroke-linejoin',
     'stroke-miterlimit',
     'stroke-opacity',
     'stroke-width',
     'systemLanguage',
     'target',
     'text-anchor',
     'to',
     'transform',
     'type',
     'u1',
     'u2',
     'underline-position',
     'underline-thickness',
     'unicode',
     'unicode-range',
     'units-per-em',
     'values',
     'version',
     'viewBox',
     'visibility',
     'width',
     'widths',
     'x',
     'x-height',
     'x1',
     'x2',
     'xlink:actuate',
     'xlink:arcrole',
     'xlink:href',
     'xlink:role',
     'xlink:show',
     'xlink:title',
     'xlink:type',
     'xml:base',
     'xml:lang',
     'xml:space',
     'xmlns',
     'xmlns:xlink',
     'y',
     'y1',
     'y2',
     'zoomAndPan'])
    svg_attr_map = None
    svg_elem_map = None
    acceptable_svg_properties = set(['fill',
     'fill-opacity',
     'fill-rule',
     'stroke',
     'stroke-width',
     'stroke-linecap',
     'stroke-linejoin',
     'stroke-opacity'])

    def reset(self):
        _BaseHTMLProcessor.reset(self)
        self.unacceptablestack = 0
        self.mathmlOK = 0
        self.svgOK = 0

    def unknown_starttag(self, tag, attrs):
        acceptable_attributes = self.acceptable_attributes
        keymap = {}
        if tag not in self.acceptable_elements or self.svgOK:
            if tag in self.unacceptable_elements_with_end_tag:
                self.unacceptablestack += 1
            if self._type.endswith('html'):
                if not dict(attrs).get('xmlns'):
                    if tag == 'svg':
                        attrs.append(('xmlns', 'http://www.w3.org/2000/svg'))
                    if tag == 'math':
                        attrs.append(('xmlns', 'http://www.w3.org/1998/Math/MathML'))
            if tag == 'math' and ('xmlns', 'http://www.w3.org/1998/Math/MathML') in attrs:
                self.mathmlOK += 1
            if tag == 'svg' and ('xmlns', 'http://www.w3.org/2000/svg') in attrs:
                self.svgOK += 1
            if self.mathmlOK and tag in self.mathml_elements:
                acceptable_attributes = self.mathml_attributes
            elif self.svgOK and tag in self.svg_elements:
                if not self.svg_attr_map:
                    lower = [ attr.lower() for attr in self.svg_attributes ]
                    mix = [ a for a in self.svg_attributes if a not in lower ]
                    self.svg_attributes = lower
                    self.svg_attr_map = dict([ (a.lower(), a) for a in mix ])
                    lower = [ attr.lower() for attr in self.svg_elements ]
                    mix = [ a for a in self.svg_elements if a not in lower ]
                    self.svg_elements = lower
                    self.svg_elem_map = dict([ (a.lower(), a) for a in mix ])
                acceptable_attributes = self.svg_attributes
                tag = self.svg_elem_map.get(tag, tag)
                keymap = self.svg_attr_map
            elif tag not in self.acceptable_elements:
                return
        if self.mathmlOK or self.svgOK:
            if filter(lambda (n, v): n.startswith('xlink:'), attrs):
                if ('xmlns:xlink', 'http://www.w3.org/1999/xlink') not in attrs:
                    attrs.append(('xmlns:xlink', 'http://www.w3.org/1999/xlink'))
        clean_attrs = []
        for key, value in self.normalize_attrs(attrs):
            if key in acceptable_attributes:
                key = keymap.get(key, key)
                if key == u'href':
                    value = _makeSafeAbsoluteURI(value)
                clean_attrs.append((key, value))
            elif key == 'style':
                clean_value = self.sanitize_style(value)
                if clean_value:
                    clean_attrs.append((key, clean_value))

        _BaseHTMLProcessor.unknown_starttag(self, tag, clean_attrs)

    def unknown_endtag(self, tag):
        if tag not in self.acceptable_elements:
            if tag in self.unacceptable_elements_with_end_tag:
                self.unacceptablestack -= 1
            if self.mathmlOK and tag in self.mathml_elements:
                if tag == 'math' and self.mathmlOK:
                    self.mathmlOK -= 1
            elif self.svgOK and tag in self.svg_elements:
                tag = self.svg_elem_map.get(tag, tag)
                if tag == 'svg' and self.svgOK:
                    self.svgOK -= 1
            else:
                return
        _BaseHTMLProcessor.unknown_endtag(self, tag)

    def handle_pi(self, text):
        pass

    def handle_decl(self, text):
        pass

    def handle_data(self, text):
        if not self.unacceptablestack:
            _BaseHTMLProcessor.handle_data(self, text)

    def sanitize_style(self, style):
        style = re.compile('url\\s*\\(\\s*[^\\s)]+?\\s*\\)\\s*').sub(' ', style)
        if not re.match('^([:,;#%.\\sa-zA-Z0-9!]|\\w-\\w|\'[\\s\\w]+\'|"[\\s\\w]+"|\\([\\d,\\s]+\\))*$', style):
            return ''
        if re.sub('\\s*[-\\w]+\\s*:\\s*[^:;]*;?', '', style).strip():
            return ''
        clean = []
        for prop, value in re.findall('([-\\w]+)\\s*:\\s*([^:;]*)', style):
            if not value:
                continue
            if prop.lower() in self.acceptable_css_properties:
                clean.append(prop + ': ' + value + ';')
            elif prop.split('-')[0].lower() in ('background', 'border', 'margin', 'padding'):
                for keyword in value.split():
                    if keyword not in self.acceptable_css_keywords and not self.valid_css_values.match(keyword):
                        break
                else:
                    clean.append(prop + ': ' + value + ';')

            elif self.svgOK and prop.lower() in self.acceptable_svg_properties:
                clean.append(prop + ': ' + value + ';')

        return ' '.join(clean)

    def parse_comment(self, i, report = 1):
        ret = _BaseHTMLProcessor.parse_comment(self, i, report)
        if ret >= 0:
            return ret
        match = re.compile('--[^>]*>').search(self.rawdata, i + 4)
        if match:
            return match.end()
        return len(self.rawdata)


def _sanitizeHTML(htmlSource, encoding, _type):
    if not _SGML_AVAILABLE:
        return htmlSource
    else:
        p = _HTMLSanitizer(encoding, _type)
        htmlSource = htmlSource.replace('<![CDATA[', '&lt;![CDATA[')
        p.feed(htmlSource)
        data = p.output()
        if TIDY_MARKUP:
            _tidy = None
            for tidy_interface in PREFERRED_TIDY_INTERFACES:
                try:
                    if tidy_interface == 'uTidy':
                        from tidy import parseString as _utidy

                        def _tidy(data, **kwargs):
                            return str(_utidy(data, **kwargs))

                        break
                    elif tidy_interface == 'mxTidy':
                        from mx.Tidy import Tidy as _mxtidy

                        def _tidy(data, **kwargs):
                            nerrors, nwarnings, data, errordata = _mxtidy.tidy(data, **kwargs)
                            return data

                        break
                except:
                    pass

            if _tidy:
                utf8 = isinstance(data, unicode)
                if utf8:
                    data = data.encode('utf-8')
                data = _tidy(data, output_xhtml=1, numeric_entities=1, wrap=0, char_encoding='utf8')
                if utf8:
                    data = unicode(data, 'utf-8')
                if data.count('<body'):
                    data = data.split('<body', 1)[1]
                    if data.count('>'):
                        data = data.split('>', 1)[1]
                if data.count('</body'):
                    data = data.split('</body', 1)[0]
        data = data.strip().replace('\r\n', '\n')
        return data


class _FeedURLHandler(urllib2.HTTPDigestAuthHandler, urllib2.HTTPRedirectHandler, urllib2.HTTPDefaultErrorHandler):

    def http_error_default(self, req, fp, code, msg, headers):
        fp.status = code
        return fp

    def http_error_301(self, req, fp, code, msg, hdrs):
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, hdrs)
        result.status = code
        result.newurl = result.geturl()
        return result

    http_error_300 = http_error_301
    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301

    def http_error_401(self, req, fp, code, msg, headers):
        host = urlparse.urlparse(req.get_full_url())[1]
        if base64 is None or 'Authorization' not in req.headers or 'WWW-Authenticate' not in headers:
            return self.http_error_default(req, fp, code, msg, headers)
        else:
            auth = _base64decode(req.headers['Authorization'].split(' ')[1])
            user, passw = auth.split(':')
            realm = re.findall('realm="([^"]*)"', headers['WWW-Authenticate'])[0]
            self.add_password(realm, host, user, passw)
            retry = self.http_error_auth_reqed('www-authenticate', host, req, headers)
            self.reset_retry_count()
            return retry


def _open_resource(url_file_stream_or_string, etag, modified, agent, referrer, handlers, request_headers):
    """URL, filename, or string --> stream
    
    This function lets you define parsers that take any input source
    (URL, pathname to local or network file, or actual data as a string)
    and deal with it in a uniform manner.  Returned object is guaranteed
    to have all the basic stdio read methods (read, readline, readlines).
    Just .close() the object when you're done with it.
    
    If the etag argument is supplied, it will be used as the value of an
    If-None-Match request header.
    
    If the modified argument is supplied, it can be a tuple of 9 integers
    (as returned by gmtime() in the standard Python time module) or a date
    string in any format supported by feedparser. Regardless, it MUST
    be in GMT (Greenwich Mean Time). It will be reformatted into an
    RFC 1123-compliant date and used as the value of an If-Modified-Since
    request header.
    
    If the agent argument is supplied, it will be used as the value of a
    User-Agent request header.
    
    If the referrer argument is supplied, it will be used as the value of a
    Referer[sic] request header.
    
    If handlers is supplied, it is a list of handlers used to build a
    urllib2 opener.
    
    if request_headers is supplied it is a dictionary of HTTP request headers
    that will override the values generated by FeedParser.
    """
    if hasattr(url_file_stream_or_string, 'read'):
        return url_file_stream_or_string
    if isinstance(url_file_stream_or_string, basestring) and urlparse.urlparse(url_file_stream_or_string)[0] in ('http', 'https', 'ftp', 'file', 'feed'):
        if url_file_stream_or_string.startswith('feed:http'):
            url_file_stream_or_string = url_file_stream_or_string[5:]
        elif url_file_stream_or_string.startswith('feed:'):
            url_file_stream_or_string = 'http:' + url_file_stream_or_string[5:]
        if not agent:
            agent = USER_AGENT
        auth = None
        if base64:
            urltype, rest = urllib.splittype(url_file_stream_or_string)
            realhost, rest = urllib.splithost(rest)
            if realhost:
                user_passwd, realhost = urllib.splituser(realhost)
                if user_passwd:
                    url_file_stream_or_string = '%s://%s%s' % (urltype, realhost, rest)
                    auth = base64.standard_b64encode(user_passwd).strip()
        if isinstance(url_file_stream_or_string, unicode):
            url_file_stream_or_string = _convert_to_idn(url_file_stream_or_string)
        request = _build_urllib2_request(url_file_stream_or_string, agent, etag, modified, referrer, auth, request_headers)
        opener = urllib2.build_opener(*tuple(handlers + [_FeedURLHandler()]))
        opener.addheaders = []
        try:
            return opener.open(request)
        finally:
            opener.close()

    try:
        return open(url_file_stream_or_string, 'rb')
    except (IOError, UnicodeEncodeError, TypeError):
        pass

    if isinstance(url_file_stream_or_string, unicode):
        return _StringIO(url_file_stream_or_string.encode('utf-8'))
    else:
        return _StringIO(url_file_stream_or_string)


def _convert_to_idn(url):
    """Convert a URL to IDN notation"""
    parts = list(urlparse.urlsplit(url))
    try:
        parts[1].encode('ascii')
    except UnicodeEncodeError:
        host = parts[1].rsplit(':', 1)
        newhost = []
        port = u''
        if len(host) == 2:
            port = host.pop()
        for h in host[0].split('.'):
            newhost.append(h.encode('idna').decode('utf-8'))

        parts[1] = '.'.join(newhost)
        if port:
            parts[1] += ':' + port
        return urlparse.urlunsplit(parts)

    return url


def _build_urllib2_request(url, agent, etag, modified, referrer, auth, request_headers):
    request = urllib2.Request(url)
    request.add_header('User-Agent', agent)
    if etag:
        request.add_header('If-None-Match', etag)
    if isinstance(modified, basestring):
        modified = _parse_date(modified)
    elif isinstance(modified, datetime.datetime):
        modified = modified.utctimetuple()
    if modified:
        short_weekdays = ['Mon',
         'Tue',
         'Wed',
         'Thu',
         'Fri',
         'Sat',
         'Sun']
        months = ['Jan',
         'Feb',
         'Mar',
         'Apr',
         'May',
         'Jun',
         'Jul',
         'Aug',
         'Sep',
         'Oct',
         'Nov',
         'Dec']
        request.add_header('If-Modified-Since', '%s, %02d %s %04d %02d:%02d:%02d GMT' % (short_weekdays[modified[6]],
         modified[2],
         months[modified[1] - 1],
         modified[0],
         modified[3],
         modified[4],
         modified[5]))
    if referrer:
        request.add_header('Referer', referrer)
    if gzip and zlib:
        request.add_header('Accept-encoding', 'gzip, deflate')
    elif gzip:
        request.add_header('Accept-encoding', 'gzip')
    elif zlib:
        request.add_header('Accept-encoding', 'deflate')
    else:
        request.add_header('Accept-encoding', '')
    if auth:
        request.add_header('Authorization', 'Basic %s' % auth)
    if ACCEPT_HEADER:
        request.add_header('Accept', ACCEPT_HEADER)
    for header_name, header_value in request_headers.items():
        request.add_header(header_name, header_value)

    request.add_header('A-IM', 'feed')
    return request


_date_handlers = []

def registerDateHandler(func):
    """Register a date handler function (takes string, returns 9-tuple date in GMT)"""
    _date_handlers.insert(0, func)


_iso8601_tmpl = ['YYYY-?MM-?DD',
 'YYYY-0MM?-?DD',
 'YYYY-MM',
 'YYYY-?OOO',
 'YY-?MM-?DD',
 'YY-?OOO',
 'YYYY',
 '-YY-?MM',
 '-OOO',
 '-YY',
 '--MM-?DD',
 '--MM',
 '---DD',
 'CC',
 '']
_iso8601_re = [ tmpl.replace('YYYY', '(?P<year>\\d{4})').replace('YY', '(?P<year>\\d\\d)').replace('MM', '(?P<month>[01]\\d)').replace('DD', '(?P<day>[0123]\\d)').replace('OOO', '(?P<ordinal>[0123]\\d\\d)').replace('CC', '(?P<century>\\d\\d$)') + '(T?(?P<hour>\\d{2}):(?P<minute>\\d{2})' + '(:(?P<second>\\d{2}))?' + '(\\.(?P<fracsecond>\\d+))?' + '(?P<tz>[+-](?P<tzhour>\\d{2})(:(?P<tzmin>\\d{2}))?|Z)?)?' for tmpl in _iso8601_tmpl ]
try:
    del tmpl
except NameError:
    pass

_iso8601_matches = [ re.compile(regex).match for regex in _iso8601_re ]
try:
    del regex
except NameError:
    pass

def _parse_date_iso8601(dateString):
    """Parse a variety of ISO-8601-compatible formats like 20040105"""
    m = None
    for _iso8601_match in _iso8601_matches:
        m = _iso8601_match(dateString)
        if m:
            break

    if not m:
        return
    elif m.span() == (0, 0):
        return
    else:
        params = m.groupdict()
        ordinal = params.get('ordinal', 0)
        if ordinal:
            ordinal = int(ordinal)
        else:
            ordinal = 0
        year = params.get('year', '--')
        if not year or year == '--':
            year = time.gmtime()[0]
        elif len(year) == 2:
            year = 100 * int(time.gmtime()[0] / 100) + int(year)
        else:
            year = int(year)
        month = params.get('month', '-')
        if not month or month == '-':
            if ordinal:
                month = 1
            else:
                month = time.gmtime()[1]
        month = int(month)
        day = params.get('day', 0)
        if not day:
            if ordinal:
                day = ordinal
            elif params.get('century', 0) or params.get('year', 0) or params.get('month', 0):
                day = 1
            else:
                day = time.gmtime()[2]
        else:
            day = int(day)
        if 'century' in params:
            year = (int(params['century']) - 1) * 100 + 1
        for field in ['hour',
         'minute',
         'second',
         'tzhour',
         'tzmin']:
            if not params.get(field, None):
                params[field] = 0

        hour = int(params.get('hour', 0))
        minute = int(params.get('minute', 0))
        second = int(float(params.get('second', 0)))
        weekday = 0
        daylight_savings_flag = -1
        tm = [year,
         month,
         day,
         hour,
         minute,
         second,
         weekday,
         ordinal,
         daylight_savings_flag]
        tz = params.get('tz')
        if tz and tz != 'Z':
            if tz[0] == '-':
                tm[3] += int(params.get('tzhour', 0))
                tm[4] += int(params.get('tzmin', 0))
            elif tz[0] == '+':
                tm[3] -= int(params.get('tzhour', 0))
                tm[4] -= int(params.get('tzmin', 0))
            else:
                return
        return time.localtime(time.mktime(tuple(tm)))


registerDateHandler(_parse_date_iso8601)
_korean_year = u'\ub144'
_korean_month = u'\uc6d4'
_korean_day = u'\uc77c'
_korean_am = u'\uc624\uc804'
_korean_pm = u'\uc624\ud6c4'
_korean_onblog_date_re = re.compile('(\\d{4})%s\\s+(\\d{2})%s\\s+(\\d{2})%s\\s+(\\d{2}):(\\d{2}):(\\d{2})' % (_korean_year, _korean_month, _korean_day))
_korean_nate_date_re = re.compile(u'(\\d{4})-(\\d{2})-(\\d{2})\\s+(%s|%s)\\s+(\\d{,2}):(\\d{,2}):(\\d{,2})' % (_korean_am, _korean_pm))

def _parse_date_onblog(dateString):
    """Parse a string according to the OnBlog 8-bit date format"""
    m = _korean_onblog_date_re.match(dateString)
    if not m:
        return
    w3dtfdate = '%(year)s-%(month)s-%(day)sT%(hour)s:%(minute)s:%(second)s%(zonediff)s' % {'year': m.group(1),
     'month': m.group(2),
     'day': m.group(3),
     'hour': m.group(4),
     'minute': m.group(5),
     'second': m.group(6),
     'zonediff': '+09:00'}
    return _parse_date_w3dtf(w3dtfdate)


registerDateHandler(_parse_date_onblog)

def _parse_date_nate(dateString):
    """Parse a string according to the Nate 8-bit date format"""
    m = _korean_nate_date_re.match(dateString)
    if not m:
        return
    hour = int(m.group(5))
    ampm = m.group(4)
    if ampm == _korean_pm:
        hour += 12
    hour = str(hour)
    if len(hour) == 1:
        hour = '0' + hour
    w3dtfdate = '%(year)s-%(month)s-%(day)sT%(hour)s:%(minute)s:%(second)s%(zonediff)s' % {'year': m.group(1),
     'month': m.group(2),
     'day': m.group(3),
     'hour': hour,
     'minute': m.group(6),
     'second': m.group(7),
     'zonediff': '+09:00'}
    return _parse_date_w3dtf(w3dtfdate)


registerDateHandler(_parse_date_nate)
_greek_months = {u'\u0399\u03b1\u03bd': u'Jan',
 u'\u03a6\u03b5\u03b2': u'Feb',
 u'\u039c\u03ac\u03ce': u'Mar',
 u'\u039c\u03b1\u03ce': u'Mar',
 u'\u0391\u03c0\u03c1': u'Apr',
 u'\u039c\u03ac\u03b9': u'May',
 u'\u039c\u03b1\u03ca': u'May',
 u'\u039c\u03b1\u03b9': u'May',
 u'\u0399\u03bf\u03cd\u03bd': u'Jun',
 u'\u0399\u03bf\u03bd': u'Jun',
 u'\u0399\u03bf\u03cd\u03bb': u'Jul',
 u'\u0399\u03bf\u03bb': u'Jul',
 u'\u0391\u03cd\u03b3': u'Aug',
 u'\u0391\u03c5\u03b3': u'Aug',
 u'\u03a3\u03b5\u03c0': u'Sep',
 u'\u039f\u03ba\u03c4': u'Oct',
 u'\u039d\u03bf\u03ad': u'Nov',
 u'\u039d\u03bf\u03b5': u'Nov',
 u'\u0394\u03b5\u03ba': u'Dec'}
_greek_wdays = {u'\u039a\u03c5\u03c1': u'Sun',
 u'\u0394\u03b5\u03c5': u'Mon',
 u'\u03a4\u03c1\u03b9': u'Tue',
 u'\u03a4\u03b5\u03c4': u'Wed',
 u'\u03a0\u03b5\u03bc': u'Thu',
 u'\u03a0\u03b1\u03c1': u'Fri',
 u'\u03a3\u03b1\u03b2': u'Sat'}
_greek_date_format_re = re.compile(u'([^,]+),\\s+(\\d{2})\\s+([^\\s]+)\\s+(\\d{4})\\s+(\\d{2}):(\\d{2}):(\\d{2})\\s+([^\\s]+)')

def _parse_date_greek(dateString):
    """Parse a string according to a Greek 8-bit date format."""
    m = _greek_date_format_re.match(dateString)
    if not m:
        return
    wday = _greek_wdays[m.group(1)]
    month = _greek_months[m.group(3)]
    rfc822date = '%(wday)s, %(day)s %(month)s %(year)s %(hour)s:%(minute)s:%(second)s %(zonediff)s' % {'wday': wday,
     'day': m.group(2),
     'month': month,
     'year': m.group(4),
     'hour': m.group(5),
     'minute': m.group(6),
     'second': m.group(7),
     'zonediff': m.group(8)}
    return _parse_date_rfc822(rfc822date)


registerDateHandler(_parse_date_greek)
_hungarian_months = {u'janu\xe1r': u'01',
 u'febru\xe1ri': u'02',
 u'm\xe1rcius': u'03',
 u'\xe1prilis': u'04',
 u'm\xe1ujus': u'05',
 u'j\xfanius': u'06',
 u'j\xfalius': u'07',
 u'augusztus': u'08',
 u'szeptember': u'09',
 u'okt\xf3ber': u'10',
 u'november': u'11',
 u'december': u'12'}
_hungarian_date_format_re = re.compile(u'(\\d{4})-([^-]+)-(\\d{,2})T(\\d{,2}):(\\d{2})((\\+|-)(\\d{,2}:\\d{2}))')

def _parse_date_hungarian(dateString):
    """Parse a string according to a Hungarian 8-bit date format."""
    m = _hungarian_date_format_re.match(dateString)
    if not m or m.group(2) not in _hungarian_months:
        return None
    else:
        month = _hungarian_months[m.group(2)]
        day = m.group(3)
        if len(day) == 1:
            day = '0' + day
        hour = m.group(4)
        if len(hour) == 1:
            hour = '0' + hour
        w3dtfdate = '%(year)s-%(month)s-%(day)sT%(hour)s:%(minute)s%(zonediff)s' % {'year': m.group(1),
         'month': month,
         'day': day,
         'hour': hour,
         'minute': m.group(5),
         'zonediff': m.group(6)}
        return _parse_date_w3dtf(w3dtfdate)


registerDateHandler(_parse_date_hungarian)

def _parse_date_w3dtf(dateString):

    def __extract_date(m):
        year = int(m.group('year'))
        if year < 100:
            year = 100 * int(time.gmtime()[0] / 100) + int(year)
        if year < 1000:
            return (0, 0, 0)
        else:
            julian = m.group('julian')
            if julian:
                julian = int(julian)
                month = julian / 30 + 1
                day = julian % 30 + 1
                jday = None
                while jday != julian:
                    t = time.mktime((year,
                     month,
                     day,
                     0,
                     0,
                     0,
                     0,
                     0,
                     0))
                    jday = time.gmtime(t)[-2]
                    diff = abs(jday - julian)
                    if jday > julian:
                        if diff < day:
                            day = day - diff
                        else:
                            month = month - 1
                            day = 31
                    elif jday < julian:
                        if day + diff < 28:
                            day = day + diff
                        else:
                            month = month + 1

                return (year, month, day)
            month = m.group('month')
            day = 1
            if month is None:
                month = 1
            else:
                month = int(month)
                day = m.group('day')
                if day:
                    day = int(day)
                else:
                    day = 1
            return (year, month, day)

    def __extract_time(m):
        if not m:
            return (0, 0, 0)
        hours = m.group('hours')
        if not hours:
            return (0, 0, 0)
        hours = int(hours)
        minutes = int(m.group('minutes'))
        seconds = m.group('seconds')
        if seconds:
            seconds = int(seconds)
        else:
            seconds = 0
        return (hours, minutes, seconds)

    def __extract_tzd(m):
        """Return the Time Zone Designator as an offset in seconds from UTC."""
        if not m:
            return 0
        tzd = m.group('tzd')
        if not tzd:
            return 0
        if tzd == 'Z':
            return 0
        hours = int(m.group('tzdhours'))
        minutes = m.group('tzdminutes')
        if minutes:
            minutes = int(minutes)
        else:
            minutes = 0
        offset = (hours * 60 + minutes) * 60
        if tzd[0] == '+':
            return -offset
        return offset

    __date_re = '(?P<year>\\d\\d\\d\\d)(?:(?P<dsep>-|)(?:(?P<month>\\d\\d)(?:(?P=dsep)(?P<day>\\d\\d))?|(?P<julian>\\d\\d\\d)))?'
    __tzd_re = ' ?(?P<tzd>[-+](?P<tzdhours>\\d\\d)(?::?(?P<tzdminutes>\\d\\d))|Z)?'
    __time_re = '(?P<hours>\\d\\d)(?P<tsep>:|)(?P<minutes>\\d\\d)(?:(?P=tsep)(?P<seconds>\\d\\d)(?:[.,]\\d+)?)?' + __tzd_re
    __datetime_re = '%s(?:[T ]%s)?' % (__date_re, __time_re)
    __datetime_rx = re.compile(__datetime_re)
    m = __datetime_rx.match(dateString)
    if m is None or m.group() != dateString:
        return
    else:
        gmt = __extract_date(m) + __extract_time(m) + (0, 0, 0)
        if gmt[0] == 0:
            return
        return time.gmtime(time.mktime(gmt) + __extract_tzd(m) - time.timezone)


registerDateHandler(_parse_date_w3dtf)
_rfc822_months = ['jan',
 'feb',
 'mar',
 'apr',
 'may',
 'jun',
 'jul',
 'aug',
 'sep',
 'oct',
 'nov',
 'dec']
_rfc822_daynames = ['mon',
 'tue',
 'wed',
 'thu',
 'fri',
 'sat',
 'sun']
_rfc822_month = '(?P<month>%s)(?:[a-z]*,?)' % '|'.join(_rfc822_months)
_rfc822_year = '(?P<year>(?:\\d{2})?\\d{2})'
_rfc822_day = '(?P<day> *\\d{1,2})'
_rfc822_date = '%s %s %s' % (_rfc822_day, _rfc822_month, _rfc822_year)
_rfc822_hour = '(?P<hour>\\d{2}):(?P<minute>\\d{2})(?::(?P<second>\\d{2}))?'
_rfc822_tz = '(?P<tz>ut|gmt(?:[+-]\\d{2}:\\d{2})?|[aecmp][sd]?t|[zamny]|[+-]\\d{4})'
_rfc822_tznames = {'ut': 0,
 'gmt': 0,
 'z': 0,
 'adt': -3,
 'ast': -4,
 'at': -4,
 'edt': -4,
 'est': -5,
 'et': -5,
 'cdt': -5,
 'cst': -6,
 'ct': -6,
 'mdt': -6,
 'mst': -7,
 'mt': -7,
 'pdt': -7,
 'pst': -8,
 'pt': -8,
 'a': -1,
 'n': 1,
 'm': -12,
 'y': 12}
_rfc822_time = '%s (?:etc/)?%s' % (_rfc822_hour, _rfc822_tz)
_rfc822_dayname = '(?P<dayname>%s)' % '|'.join(_rfc822_daynames)
_rfc822_match = re.compile('(?:%s, )?%s(?: %s)?' % (_rfc822_dayname, _rfc822_date, _rfc822_time)).match

def _parse_date_rfc822(dt):
    """Parse RFC 822 dates and times, with one minor
    difference: years may be 4DIGIT or 2DIGIT.
    http://tools.ietf.org/html/rfc822#section-5"""
    try:
        m = _rfc822_match(dt.lower()).groupdict(0)
    except AttributeError:
        return None

    for k in ('year', 'day', 'hour', 'minute', 'second'):
        m[k] = int(m[k])

    m['month'] = _rfc822_months.index(m['month']) + 1
    if m['year'] < 100:
        m['year'] += (1900, 2000)[m['year'] < 90]
    stamp = datetime.datetime(*[ m[i] for i in ('year', 'month', 'day', 'hour', 'minute', 'second') ])
    tzhour = 0
    tzmin = 0
    if m['tz'] and m['tz'].startswith('gmt'):
        m['tz'] = ''.join(m['tz'][3:].split(':')) or 'gmt'
    if not m['tz']:
        pass
    elif m['tz'].startswith('+'):
        tzhour = int(m['tz'][1:3])
        tzmin = int(m['tz'][3:])
    elif m['tz'].startswith('-'):
        tzhour = int(m['tz'][1:3]) * -1
        tzmin = int(m['tz'][3:]) * -1
    else:
        tzhour = _rfc822_tznames[m['tz']]
    delta = datetime.timedelta(0, 0, 0, 0, tzmin, tzhour)
    return (stamp - delta).utctimetuple()


registerDateHandler(_parse_date_rfc822)

def _parse_date_asctime(dt):
    """Parse asctime-style dates"""
    dayname, month, day, remainder = dt.split(None, 3)
    month = '%02i ' % (_rfc822_months.index(month.lower()) + 1)
    day = '%02i ' % (int(day),)
    dt = month + day + remainder
    return time.strptime(dt, '%m %d %H:%M:%S %Y')[:-1] + (0,)


registerDateHandler(_parse_date_asctime)

def _parse_date_perforce(aDateString):
    """parse a date in yyyy/mm/dd hh:mm:ss TTT format"""
    _my_date_pattern = re.compile('(\\w{,3}), (\\d{,4})/(\\d{,2})/(\\d{2}) (\\d{,2}):(\\d{2}):(\\d{2}) (\\w{,3})')
    m = _my_date_pattern.search(aDateString)
    if m is None:
        return
    dow, year, month, day, hour, minute, second, tz = m.groups()
    months = ['Jan',
     'Feb',
     'Mar',
     'Apr',
     'May',
     'Jun',
     'Jul',
     'Aug',
     'Sep',
     'Oct',
     'Nov',
     'Dec']
    dateString = '%s, %s %s %s %s:%s:%s %s' % (dow,
     day,
     months[int(month) - 1],
     year,
     hour,
     minute,
     second,
     tz)
    tm = rfc822.parsedate_tz(dateString)
    if tm:
        return time.gmtime(rfc822.mktime_tz(tm))
    else:
        return


registerDateHandler(_parse_date_perforce)

def _parse_date(dateString):
    """Parses a variety of date formats into a 9-tuple in GMT"""
    if not dateString:
        return None
    else:
        for handler in _date_handlers:
            try:
                date9tuple = handler(dateString)
            except (KeyError, OverflowError, ValueError):
                continue

            if not date9tuple:
                continue
            if len(date9tuple) != 9:
                continue
            return date9tuple

        return None


def _getCharacterEncoding(http_headers, xml_data):
    """Get the character encoding of the XML document
    
    http_headers is a dictionary
    xml_data is a raw string (not Unicode)
    
    This is so much trickier than it sounds, it's not even funny.
    According to RFC 3023 ('XML Media Types'), if the HTTP Content-Type
    is application/xml, application/*+xml,
    application/xml-external-parsed-entity, or application/xml-dtd,
    the encoding given in the charset parameter of the HTTP Content-Type
    takes precedence over the encoding given in the XML prefix within the
    document, and defaults to 'utf-8' if neither are specified.  But, if
    the HTTP Content-Type is text/xml, text/*+xml, or
    text/xml-external-parsed-entity, the encoding given in the XML prefix
    within the document is ALWAYS IGNORED and only the encoding given in
    the charset parameter of the HTTP Content-Type header should be
    respected, and it defaults to 'us-ascii' if not specified.
    
    Furthermore, discussion on the atom-syntax mailing list with the
    author of RFC 3023 leads me to the conclusion that any document
    served with a Content-Type of text/* and no charset parameter
    must be treated as us-ascii.  (We now do this.)  And also that it
    must always be flagged as non-well-formed.  (We now do this too.)
    
    If Content-Type is unspecified (input was local file or non-HTTP source)
    or unrecognized (server just got it totally wrong), then go by the
    encoding given in the XML prefix of the document and default to
    'iso-8859-1' as per the HTTP specification (RFC 2616).
    
    Then, assuming we didn't find a character encoding in the HTTP headers
    (and the HTTP Content-type allowed us to look in the body), we need
    to sniff the first few bytes of the XML data and try to determine
    whether the encoding is ASCII-compatible.  Section F of the XML
    specification shows the way here:
    http://www.w3.org/TR/REC-xml/#sec-guessing-no-ext-info
    
    If the sniffed encoding is not ASCII-compatible, we need to make it
    ASCII compatible so that we can sniff further into the XML declaration
    to find the encoding attribute, which will tell us the true encoding.
    
    Of course, none of this guarantees that we will be able to parse the
    feed in the declared character encoding (assuming it was declared
    correctly, which many are not).  iconv_codec can help a lot;
    you should definitely install it if you can.
    http://cjkpython.i18n.org/
    """

    def _parseHTTPContentType(content_type):
        """takes HTTP Content-Type header and returns (content type, charset)
        
        If no charset is specified, returns (content type, '')
        If no content type is specified, returns ('', '')
        Both return parameters are guaranteed to be lowercase strings
        """
        content_type = content_type or ''
        content_type, params = cgi.parse_header(content_type)
        charset = params.get('charset', '').replace("'", '')
        if not isinstance(charset, unicode):
            charset = charset.decode('utf-8', 'ignore')
        return (content_type, charset)

    sniffed_xml_encoding = u''
    xml_encoding = u''
    true_encoding = u''
    http_content_type, http_encoding = _parseHTTPContentType(http_headers.get('content-type'))
    try:
        if xml_data[:4] == _l2bytes([76,
         111,
         167,
         148]):
            sniffed_xml_encoding = u'cp037'
            xml_data = xml_data.decode('cp037').encode('utf-8')
        elif xml_data[:4] == _l2bytes([0,
         60,
         0,
         63]):
            sniffed_xml_encoding = u'utf-16be'
            xml_data = unicode(xml_data, 'utf-16be').encode('utf-8')
        elif len(xml_data) >= 4 and xml_data[:2] == _l2bytes([254, 255]) and xml_data[2:4] != _l2bytes([0, 0]):
            sniffed_xml_encoding = u'utf-16be'
            xml_data = unicode(xml_data[2:], 'utf-16be').encode('utf-8')
        elif xml_data[:4] == _l2bytes([60,
         0,
         63,
         0]):
            sniffed_xml_encoding = u'utf-16le'
            xml_data = unicode(xml_data, 'utf-16le').encode('utf-8')
        elif len(xml_data) >= 4 and xml_data[:2] == _l2bytes([255, 254]) and xml_data[2:4] != _l2bytes([0, 0]):
            sniffed_xml_encoding = u'utf-16le'
            xml_data = unicode(xml_data[2:], 'utf-16le').encode('utf-8')
        elif xml_data[:4] == _l2bytes([0,
         0,
         0,
         60]):
            sniffed_xml_encoding = u'utf-32be'
            if _UTF32_AVAILABLE:
                xml_data = unicode(xml_data, 'utf-32be').encode('utf-8')
        elif xml_data[:4] == _l2bytes([60,
         0,
         0,
         0]):
            sniffed_xml_encoding = u'utf-32le'
            if _UTF32_AVAILABLE:
                xml_data = unicode(xml_data, 'utf-32le').encode('utf-8')
        elif xml_data[:4] == _l2bytes([0,
         0,
         254,
         255]):
            sniffed_xml_encoding = u'utf-32be'
            if _UTF32_AVAILABLE:
                xml_data = unicode(xml_data[4:], 'utf-32be').encode('utf-8')
        elif xml_data[:4] == _l2bytes([255,
         254,
         0,
         0]):
            sniffed_xml_encoding = u'utf-32le'
            if _UTF32_AVAILABLE:
                xml_data = unicode(xml_data[4:], 'utf-32le').encode('utf-8')
        elif xml_data[:3] == _l2bytes([239, 187, 191]):
            sniffed_xml_encoding = u'utf-8'
            xml_data = unicode(xml_data[3:], 'utf-8').encode('utf-8')
        xml_encoding_match = re.compile(_s2bytes('^<\\?.*encoding=[\'"](.*?)[\'"].*\\?>')).match(xml_data)
    except UnicodeDecodeError:
        xml_encoding_match = None

    if xml_encoding_match:
        xml_encoding = xml_encoding_match.groups()[0].decode('utf-8').lower()
        if sniffed_xml_encoding and xml_encoding in (u'iso-10646-ucs-2', u'ucs-2', u'csunicode', u'iso-10646-ucs-4', u'ucs-4', u'csucs4', u'utf-16', u'utf-32', u'utf_16', u'utf_32', u'utf16', u'u16'):
            xml_encoding = sniffed_xml_encoding
    acceptable_content_type = 0
    application_content_types = (u'application/xml', u'application/xml-dtd', u'application/xml-external-parsed-entity')
    text_content_types = (u'text/xml', u'text/xml-external-parsed-entity')
    if http_content_type in application_content_types or http_content_type.startswith(u'application/') and http_content_type.endswith(u'+xml'):
        acceptable_content_type = 1
        true_encoding = http_encoding or xml_encoding or u'utf-8'
    elif http_content_type in text_content_types or http_content_type.startswith(u'text/') and http_content_type.endswith(u'+xml'):
        acceptable_content_type = 1
        true_encoding = http_encoding or u'us-ascii'
    elif http_content_type.startswith(u'text/'):
        true_encoding = http_encoding or u'us-ascii'
    elif http_headers and 'content-type' not in http_headers:
        true_encoding = xml_encoding or u'iso-8859-1'
    else:
        true_encoding = xml_encoding or u'utf-8'
    if true_encoding.lower() == u'gb2312':
        true_encoding = u'gb18030'
    return (true_encoding,
     http_encoding,
     xml_encoding,
     sniffed_xml_encoding,
     acceptable_content_type)


def _toUTF8(data, encoding):
    """Changes an XML data stream on the fly to specify a new encoding
    
    data is a raw sequence of bytes (not Unicode) that is presumed to be in %encoding already
    encoding is a string recognized by encodings.aliases
    """
    if len(data) >= 4 and data[:2] == _l2bytes([254, 255]) and data[2:4] != _l2bytes([0, 0]):
        encoding = 'utf-16be'
        data = data[2:]
    elif len(data) >= 4 and data[:2] == _l2bytes([255, 254]) and data[2:4] != _l2bytes([0, 0]):
        encoding = 'utf-16le'
        data = data[2:]
    elif data[:3] == _l2bytes([239, 187, 191]):
        encoding = 'utf-8'
        data = data[3:]
    elif data[:4] == _l2bytes([0,
     0,
     254,
     255]):
        encoding = 'utf-32be'
        data = data[4:]
    elif data[:4] == _l2bytes([255,
     254,
     0,
     0]):
        encoding = 'utf-32le'
        data = data[4:]
    newdata = unicode(data, encoding)
    declmatch = re.compile('^<\\?xml[^>]*?>')
    newdecl = "<?xml version='1.0' encoding='utf-8'?>"
    if declmatch.search(newdata):
        newdata = declmatch.sub(newdecl, newdata)
    else:
        newdata = newdecl + u'\n' + newdata
    return newdata.encode('utf-8')


def _stripDoctype(data):
    """Strips DOCTYPE from XML document, returns (rss_version, stripped_data)
    
    rss_version may be 'rss091n' or None
    stripped_data is the same XML document, minus the DOCTYPE
    """
    start = re.search(_s2bytes('<\\w'), data)
    start = start and start.start() or -1
    head, data = data[:start + 1], data[start + 1:]
    entity_pattern = re.compile(_s2bytes('^\\s*<!ENTITY([^>]*?)>'), re.MULTILINE)
    entity_results = entity_pattern.findall(head)
    head = entity_pattern.sub(_s2bytes(''), head)
    doctype_pattern = re.compile(_s2bytes('^\\s*<!DOCTYPE([^>]*?)>'), re.MULTILINE)
    doctype_results = doctype_pattern.findall(head)
    doctype = doctype_results and doctype_results[0] or _s2bytes('')
    if doctype.lower().count(_s2bytes('netscape')):
        version = u'rss091n'
    else:
        version = None
    replacement = _s2bytes('')
    if len(doctype_results) == 1 and entity_results:
        safe_pattern = re.compile(_s2bytes('\\s+(\\w+)\\s+"(&#\\w+;|[^&"]*)"'))
        safe_entities = filter(lambda e: safe_pattern.match(e), entity_results)
        if safe_entities:
            replacement = _s2bytes('<!DOCTYPE feed [\n  <!ENTITY') + _s2bytes('>\n  <!ENTITY ').join(safe_entities) + _s2bytes('>\n]>')
    data = doctype_pattern.sub(replacement, head) + data
    return (version, data, dict(replacement and [ (k.decode('utf-8'), v.decode('utf-8')) for k, v in safe_pattern.findall(replacement) ]))


def parse(url_file_stream_or_string, etag = None, modified = None, agent = None, referrer = None, handlers = None, request_headers = None, response_headers = None):
    """Parse a feed from a URL, file, stream, or string.
    
    request_headers, if given, is a dict from http header name to value to add
    to the request; this overrides internally generated values.
    """
    if handlers is None:
        handlers = []
    if request_headers is None:
        request_headers = {}
    if response_headers is None:
        response_headers = {}
    result = FeedParserDict()
    result['feed'] = FeedParserDict()
    result['entries'] = []
    result['bozo'] = 0
    if not isinstance(handlers, list):
        handlers = [handlers]
    try:
        f = _open_resource(url_file_stream_or_string, etag, modified, agent, referrer, handlers, request_headers)
        data = f.read()
    except Exception as e:
        result['bozo'] = 1
        result['bozo_exception'] = e
        data = None
        f = None

    if hasattr(f, 'headers'):
        result['headers'] = dict(f.headers)
    if 'headers' in result:
        result['headers'].update(response_headers)
    elif response_headers:
        result['headers'] = copy.deepcopy(response_headers)
    if 'headers' in result:
        http_headers = dict(((k.lower(), v) for k, v in result['headers'].items()))
    else:
        http_headers = {}
    if f and data and http_headers:
        if gzip and 'gzip' in http_headers.get('content-encoding', ''):
            try:
                data = gzip.GzipFile(fileobj=_StringIO(data)).read()
            except (IOError, struct.error) as e:
                result['bozo'] = 1
                result['bozo_exception'] = e
                if isinstance(e, struct.error):
                    data = None

        elif zlib and 'deflate' in http_headers.get('content-encoding', ''):
            try:
                data = zlib.decompress(data)
            except zlib.error as e:
                try:
                    data = zlib.decompress(data, -15)
                except zlib.error as e:
                    result['bozo'] = 1
                    result['bozo_exception'] = e

    if http_headers:
        if 'etag' in http_headers:
            etag = http_headers.get('etag', u'')
            if not isinstance(etag, unicode):
                etag = etag.decode('utf-8', 'ignore')
            if etag:
                result['etag'] = etag
        if 'last-modified' in http_headers:
            modified = http_headers.get('last-modified', u'')
            if modified:
                result['modified'] = modified
                result['modified_parsed'] = _parse_date(modified)
    if hasattr(f, 'url'):
        if not isinstance(f.url, unicode):
            result['href'] = f.url.decode('utf-8', 'ignore')
        else:
            result['href'] = f.url
        result['status'] = 200
    if hasattr(f, 'status'):
        result['status'] = f.status
    if hasattr(f, 'close'):
        f.close()
    if data is None:
        return result
    else:
        result['encoding'], http_encoding, xml_encoding, sniffed_xml_encoding, acceptable_content_type = _getCharacterEncoding(http_headers, data)
        if http_headers and not acceptable_content_type:
            if 'content-type' in http_headers:
                bozo_message = '%s is not an XML media type' % http_headers['content-type']
            else:
                bozo_message = 'no Content-type specified'
            result['bozo'] = 1
            result['bozo_exception'] = NonXMLContentType(bozo_message)
        contentloc = http_headers.get('content-location', u'')
        href = result.get('href', u'')
        baseuri = _makeSafeAbsoluteURI(href, contentloc) or _makeSafeAbsoluteURI(contentloc) or href
        baselang = http_headers.get('content-language', None)
        if not isinstance(baselang, unicode) and baselang is not None:
            baselang = baselang.decode('utf-8', 'ignore')
        if getattr(f, 'code', 0) == 304:
            result['version'] = u''
            result['debug_message'] = 'The feed has not changed since you last checked, ' + 'so the server sent no data.  This is a feature, not a bug!'
            return result
        if data is None:
            return result
        use_strict_parser = 0
        known_encoding = 0
        tried_encodings = []
        for proposed_encoding in (result['encoding'], xml_encoding, sniffed_xml_encoding):
            if not proposed_encoding:
                continue
            if proposed_encoding in tried_encodings:
                continue
            tried_encodings.append(proposed_encoding)
            try:
                data = _toUTF8(data, proposed_encoding)
            except (UnicodeDecodeError, LookupError):
                pass
            else:
                known_encoding = use_strict_parser = 1
                break

        if not known_encoding and chardet:
            proposed_encoding = unicode(chardet.detect(data)['encoding'], 'ascii', 'ignore')
            if proposed_encoding and proposed_encoding not in tried_encodings:
                tried_encodings.append(proposed_encoding)
                try:
                    data = _toUTF8(data, proposed_encoding)
                except (UnicodeDecodeError, LookupError):
                    pass
                else:
                    known_encoding = use_strict_parser = 1

        if not known_encoding and u'utf-8' not in tried_encodings:
            proposed_encoding = u'utf-8'
            tried_encodings.append(proposed_encoding)
            try:
                data = _toUTF8(data, proposed_encoding)
            except UnicodeDecodeError:
                pass
            else:
                known_encoding = use_strict_parser = 1

        if not known_encoding and u'windows-1252' not in tried_encodings:
            proposed_encoding = u'windows-1252'
            tried_encodings.append(proposed_encoding)
            try:
                data = _toUTF8(data, proposed_encoding)
            except UnicodeDecodeError:
                pass
            else:
                known_encoding = use_strict_parser = 1

        if not known_encoding and u'iso-8859-2' not in tried_encodings:
            proposed_encoding = u'iso-8859-2'
            tried_encodings.append(proposed_encoding)
            try:
                data = _toUTF8(data, proposed_encoding)
            except UnicodeDecodeError:
                pass
            else:
                known_encoding = use_strict_parser = 1

        if not known_encoding:
            result['bozo'] = 1
            result['bozo_exception'] = CharacterEncodingUnknown('document encoding unknown, I tried ' + '%s, %s, utf-8, windows-1252, and iso-8859-2 but nothing worked' % (result['encoding'], xml_encoding))
            result['encoding'] = u''
        elif proposed_encoding != result['encoding']:
            result['bozo'] = 1
            result['bozo_exception'] = CharacterEncodingOverride('document declared as %s, but parsed as %s' % (result['encoding'], proposed_encoding))
            result['encoding'] = proposed_encoding
        result['version'], data, entities = _stripDoctype(data)
        if not _XML_AVAILABLE:
            use_strict_parser = 0
        if use_strict_parser:
            feedparser = _StrictFeedParser(baseuri, baselang, 'utf-8')
            saxparser = xml.sax.make_parser(PREFERRED_XML_PARSERS)
            saxparser.setFeature(xml.sax.handler.feature_namespaces, 1)
            try:
                saxparser.setFeature(xml.sax.handler.feature_external_ges, 0)
            except xml.sax.SAXNotSupportedException:
                pass

            saxparser.setContentHandler(feedparser)
            saxparser.setErrorHandler(feedparser)
            source = xml.sax.xmlreader.InputSource()
            source.setByteStream(_StringIO(data))
            try:
                saxparser.parse(source)
            except xml.sax.SAXParseException as e:
                result['bozo'] = 1
                result['bozo_exception'] = feedparser.exc or e
                use_strict_parser = 0

        if not use_strict_parser and _SGML_AVAILABLE:
            feedparser = _LooseFeedParser(baseuri, baselang, 'utf-8', entities)
            feedparser.feed(data.decode('utf-8', 'replace'))
        result['feed'] = feedparser.feeddata
        result['entries'] = feedparser.entries
        result['version'] = result['version'] or feedparser.version
        result['namespaces'] = feedparser.namespacesInUse
        return result
