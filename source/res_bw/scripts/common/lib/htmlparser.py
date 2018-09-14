# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/HTMLParser.py
"""A parser for HTML and XHTML."""
import markupbase
import re
interesting_normal = re.compile('[&<]')
incomplete = re.compile('&[a-zA-Z#]')
entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*)[^a-zA-Z0-9]')
charref = re.compile('&#(?:[0-9]+|[xX][0-9a-fA-F]+)[^0-9a-fA-F]')
starttagopen = re.compile('<[a-zA-Z]')
piclose = re.compile('>')
commentclose = re.compile('--\\s*>')
tagfind = re.compile('([a-zA-Z][^\t\n\r\x0c />\x00]*)(?:\\s|/(?!>))*')
tagfind_tolerant = re.compile('[a-zA-Z][^\t\n\r\x0c />\x00]*')
attrfind = re.compile('((?<=[\\\'"\\s/])[^\\s/>][^\\s/=>]*)(\\s*=+\\s*(\\\'[^\\\']*\\\'|"[^"]*"|(?![\\\'"])[^>\\s]*))?(?:\\s|/(?!>))*')
locatestarttagend = re.compile('\n  <[a-zA-Z][^\\t\\n\\r\\f />\\x00]*       # tag name\n  (?:[\\s/]*                          # optional whitespace before attribute name\n    (?:(?<=[\'"\\s/])[^\\s/>][^\\s/=>]*  # attribute name\n      (?:\\s*=+\\s*                    # value indicator\n        (?:\'[^\']*\'                   # LITA-enclosed value\n          |"[^"]*"                   # LIT-enclosed value\n          |(?![\'"])[^>\\s]*           # bare value\n         )\n       )?(?:\\s|/(?!>))*\n     )*\n   )?\n  \\s*                                # trailing whitespace\n', re.VERBOSE)
endendtag = re.compile('>')
endtagfind = re.compile('</\\s*([a-zA-Z][-.a-zA-Z0-9:_]*)\\s*>')

class HTMLParseError(Exception):
    """Exception raised for all parse errors."""

    def __init__(self, msg, position=(None, None)):
        assert msg
        self.msg = msg
        self.lineno = position[0]
        self.offset = position[1]

    def __str__(self):
        result = self.msg
        if self.lineno is not None:
            result = result + ', at line %d' % self.lineno
        if self.offset is not None:
            result = result + ', column %d' % (self.offset + 1)
        return result


class HTMLParser(markupbase.ParserBase):
    """Find tags and other markup and call handler functions.
    
    Usage:
        p = HTMLParser()
        p.feed(data)
        ...
        p.close()
    
    Start tags are handled by calling self.handle_starttag() or
    self.handle_startendtag(); end tags by self.handle_endtag().  The
    data between tags is passed from the parser to the derived class
    by calling self.handle_data() with the data as argument (the data
    may be split up in arbitrary chunks).  Entity references are
    passed by calling self.handle_entityref() with the entity
    reference as the argument.  Numeric character references are
    passed to self.handle_charref() with the string containing the
    reference as the argument.
    """
    CDATA_CONTENT_ELEMENTS = ('script', 'style')

    def __init__(self):
        """Initialize and reset this instance."""
        self.reset()

    def reset(self):
        """Reset this instance.  Loses all unprocessed data."""
        self.rawdata = ''
        self.lasttag = '???'
        self.interesting = interesting_normal
        self.cdata_elem = None
        markupbase.ParserBase.reset(self)
        return

    def feed(self, data):
        r"""Feed data to the parser.
        
        Call this as often as you want, with as little or as much text
        as you want (may include '\n').
        """
        self.rawdata = self.rawdata + data
        self.goahead(0)

    def close(self):
        """Handle any buffered data."""
        self.goahead(1)

    def error(self, message):
        raise HTMLParseError(message, self.getpos())

    __starttag_text = None

    def get_starttag_text(self):
        """Return full source of start tag: '<...>'."""
        return self.__starttag_text

    def set_cdata_mode(self, elem):
        self.cdata_elem = elem.lower()
        self.interesting = re.compile('</\\s*%s\\s*>' % self.cdata_elem, re.I)

    def clear_cdata_mode(self):
        self.interesting = interesting_normal
        self.cdata_elem = None
        return

    def goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        while i < n:
            match = self.interesting.search(rawdata, i)
            if match:
                j = match.start()
            else:
                if self.cdata_elem:
                    break
                j = n
            if i < j:
                self.handle_data(rawdata[i:j])
            i = self.updatepos(i, j)
            if i == n:
                break
            startswith = rawdata.startswith
            if startswith('<', i):
                if starttagopen.match(rawdata, i):
                    k = self.parse_starttag(i)
                elif startswith('</', i):
                    k = self.parse_endtag(i)
                elif startswith('<!--', i):
                    k = self.parse_comment(i)
                elif startswith('<?', i):
                    k = self.parse_pi(i)
                elif startswith('<!', i):
                    k = self.parse_html_declaration(i)
                elif i + 1 < n:
                    self.handle_data('<')
                    k = i + 1
                else:
                    break
                if k < 0:
                    if not end:
                        break
                    k = rawdata.find('>', i + 1)
                    if k < 0:
                        k = rawdata.find('<', i + 1)
                        if k < 0:
                            k = i + 1
                    else:
                        k += 1
                    self.handle_data(rawdata[i:k])
                i = self.updatepos(i, k)
            if startswith('&#', i):
                match = charref.match(rawdata, i)
                if match:
                    name = match.group()[2:-1]
                    self.handle_charref(name)
                    k = match.end()
                    if not startswith(';', k - 1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    continue
                else:
                    if ';' in rawdata[i:]:
                        self.handle_data(rawdata[i:i + 2])
                        i = self.updatepos(i, i + 2)
                    break
            if startswith('&', i):
                match = entityref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    k = match.end()
                    if not startswith(';', k - 1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    continue
                match = incomplete.match(rawdata, i)
                if match:
                    if end and match.group() == rawdata[i:]:
                        self.error('EOF in middle of entity or char ref')
                    break
                elif i + 1 < n:
                    self.handle_data('&')
                    i = self.updatepos(i, i + 1)
                else:
                    break
            assert 0, 'interesting.search() lied'

        if end and i < n and not self.cdata_elem:
            self.handle_data(rawdata[i:n])
            i = self.updatepos(i, n)
        self.rawdata = rawdata[i:]

    def parse_html_declaration(self, i):
        rawdata = self.rawdata
        if rawdata[i:i + 2] != '<!':
            self.error('unexpected call to parse_html_declaration()')
        if rawdata[i:i + 4] == '<!--':
            return self.parse_comment(i)
        elif rawdata[i:i + 3] == '<![':
            return self.parse_marked_section(i)
        elif rawdata[i:i + 9].lower() == '<!doctype':
            gtpos = rawdata.find('>', i + 9)
            if gtpos == -1:
                return -1
            self.handle_decl(rawdata[i + 2:gtpos])
            return gtpos + 1
        else:
            return self.parse_bogus_comment(i)

    def parse_bogus_comment(self, i, report=1):
        rawdata = self.rawdata
        if rawdata[i:i + 2] not in ('<!', '</'):
            self.error('unexpected call to parse_comment()')
        pos = rawdata.find('>', i + 2)
        if pos == -1:
            return -1
        if report:
            self.handle_comment(rawdata[i + 2:pos])
        return pos + 1

    def parse_pi(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i + 2] == '<?', 'unexpected call to parse_pi()'
        match = piclose.search(rawdata, i + 2)
        if not match:
            return -1
        j = match.start()
        self.handle_pi(rawdata[i + 2:j])
        j = match.end()
        return j

    def parse_starttag(self, i):
        self.__starttag_text = None
        endpos = self.check_for_whole_start_tag(i)
        if endpos < 0:
            return endpos
        else:
            rawdata = self.rawdata
            self.__starttag_text = rawdata[i:endpos]
            attrs = []
            match = tagfind.match(rawdata, i + 1)
            assert match, 'unexpected call to parse_starttag()'
            k = match.end()
            self.lasttag = tag = match.group(1).lower()
            while k < endpos:
                m = attrfind.match(rawdata, k)
                if not m:
                    break
                attrname, rest, attrvalue = m.group(1, 2, 3)
                if not rest:
                    attrvalue = None
                elif not attrvalue[:1] == "'" == attrvalue[-1:]:
                    attrvalue = attrvalue[:1] == '"' == attrvalue[-1:] and attrvalue[1:-1]
                if attrvalue:
                    attrvalue = self.unescape(attrvalue)
                attrs.append((attrname.lower(), attrvalue))
                k = m.end()

            end = rawdata[k:endpos].strip()
            if end not in ('>', '/>'):
                lineno, offset = self.getpos()
                if '\n' in self.__starttag_text:
                    lineno = lineno + self.__starttag_text.count('\n')
                    offset = len(self.__starttag_text) - self.__starttag_text.rfind('\n')
                else:
                    offset = offset + len(self.__starttag_text)
                self.handle_data(rawdata[i:endpos])
                return endpos
            if end.endswith('/>'):
                self.handle_startendtag(tag, attrs)
            else:
                self.handle_starttag(tag, attrs)
                if tag in self.CDATA_CONTENT_ELEMENTS:
                    self.set_cdata_mode(tag)
            return endpos

    def check_for_whole_start_tag(self, i):
        rawdata = self.rawdata
        m = locatestarttagend.match(rawdata, i)
        if m:
            j = m.end()
            next = rawdata[j:j + 1]
            if next == '>':
                return j + 1
            if next == '/':
                if rawdata.startswith('/>', j):
                    return j + 2
                if rawdata.startswith('/', j):
                    return -1
                self.updatepos(i, j + 1)
                self.error('malformed empty start tag')
            if next == '':
                return -1
            elif next in 'abcdefghijklmnopqrstuvwxyz=/ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                return -1
            elif j > i:
                return j
            else:
                return i + 1
        raise AssertionError('we should not get here!')

    def parse_endtag(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i + 2] == '</', 'unexpected call to parse_endtag'
        match = endendtag.search(rawdata, i + 1)
        if not match:
            return -1
        else:
            gtpos = match.end()
            match = endtagfind.match(rawdata, i)
            if not match:
                if self.cdata_elem is not None:
                    self.handle_data(rawdata[i:gtpos])
                    return gtpos
                namematch = tagfind.match(rawdata, i + 2)
                if not namematch:
                    if rawdata[i:i + 3] == '</>':
                        return i + 3
                    else:
                        return self.parse_bogus_comment(i)
                tagname = namematch.group(1).lower()
                gtpos = rawdata.find('>', namematch.end())
                self.handle_endtag(tagname)
                return gtpos + 1
            elem = match.group(1).lower()
            if self.cdata_elem is not None:
                if elem != self.cdata_elem:
                    self.handle_data(rawdata[i:gtpos])
                    return gtpos
            self.handle_endtag(elem)
            self.clear_cdata_mode()
            return gtpos

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_charref(self, name):
        pass

    def handle_entityref(self, name):
        pass

    def handle_data(self, data):
        pass

    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        pass

    def handle_pi(self, data):
        pass

    def unknown_decl(self, data):
        pass

    entitydefs = None

    def unescape(self, s):
        if '&' not in s:
            return s

        def replaceEntities(s):
            s = s.groups()[0]
            try:
                if s[0] == '#':
                    s = s[1:]
                    if s[0] in ('x', 'X'):
                        c = int(s[1:], 16)
                    else:
                        c = int(s)
                    return unichr(c)
            except ValueError:
                return '&#' + s + ';'

            import htmlentitydefs
            if HTMLParser.entitydefs is None:
                entitydefs = HTMLParser.entitydefs = {'apos': u"'"}
                for k, v in htmlentitydefs.name2codepoint.iteritems():
                    entitydefs[k] = unichr(v)

            try:
                return self.entitydefs[s]
            except KeyError:
                return '&' + s + ';'

            return

        return re.sub('&(#?[xX]?(?:[0-9a-fA-F]+|\\w{1,8}));', replaceEntities, s)
