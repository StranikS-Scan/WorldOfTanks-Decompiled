# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/gettext.py
import locale, copy, os, re, struct, sys
from errno import ENOENT
__all__ = ['NullTranslations',
 'GNUTranslations',
 'Catalog',
 'find',
 'translation',
 'install',
 'textdomain',
 'bindtextdomain',
 'dgettext',
 'dngettext',
 'gettext',
 'ngettext']
_default_localedir = os.path.join(sys.prefix, 'share', 'locale')

def test(condition, true, false):
    if condition:
        return true
    else:
        return false


def c2py(plural):
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    import token, tokenize
    tokens = tokenize.generate_tokens(StringIO(plural).readline)
    try:
        danger = [ x for x in tokens if x[0] == token.NAME and x[1] != 'n' ]
    except tokenize.TokenError:
        raise ValueError, 'plural forms expression error, maybe unbalanced parenthesis'
    else:
        if danger:
            raise ValueError, 'plural forms expression could be dangerous'

    plural = plural.replace('&&', ' and ')
    plural = plural.replace('||', ' or ')
    expr = re.compile('\\!([^=])')
    plural = expr.sub(' not \\1', plural)
    expr = re.compile('(.*?)\\?(.*?):(.*)')

    def repl(x):
        return 'test(%s, %s, %s)' % (x.group(1), x.group(2), expr.sub(repl, x.group(3)))

    stack = ['']
    for c in plural:
        if c == '(':
            stack.append('')
        if c == ')':
            if len(stack) == 1:
                raise ValueError, 'unbalanced parenthesis in plural form'
            s = expr.sub(repl, stack.pop())
            stack[-1] += '(%s)' % s
        stack[-1] += c

    plural = expr.sub(repl, stack.pop())
    return eval('lambda n: int(%s)' % plural)


def _expand_lang(locale):
    from locale import normalize
    locale = normalize(locale)
    COMPONENT_CODESET = 1
    COMPONENT_TERRITORY = 2
    COMPONENT_MODIFIER = 4
    mask = 0
    pos = locale.find('@')
    if pos >= 0:
        modifier = locale[pos:]
        locale = locale[:pos]
        mask |= COMPONENT_MODIFIER
    else:
        modifier = ''
    pos = locale.find('.')
    if pos >= 0:
        codeset = locale[pos:]
        locale = locale[:pos]
        mask |= COMPONENT_CODESET
    else:
        codeset = ''
    pos = locale.find('_')
    if pos >= 0:
        territory = locale[pos:]
        locale = locale[:pos]
        mask |= COMPONENT_TERRITORY
    else:
        territory = ''
    language = locale
    ret = []
    for i in range(mask + 1):
        if not i & ~mask:
            val = language
            if i & COMPONENT_TERRITORY:
                val += territory
            if i & COMPONENT_CODESET:
                val += codeset
            if i & COMPONENT_MODIFIER:
                val += modifier
            ret.append(val)

    ret.reverse()
    return ret


class NullTranslations:

    def __init__(self, fp=None):
        self._info = {}
        self._charset = None
        self._output_charset = None
        self._fallback = None
        if fp is not None:
            self._parse(fp)
        return

    def _parse(self, fp):
        pass

    def add_fallback(self, fallback):
        if self._fallback:
            self._fallback.add_fallback(fallback)
        else:
            self._fallback = fallback

    def gettext(self, message):
        return self._fallback.gettext(message) if self._fallback else message

    def lgettext(self, message):
        return self._fallback.lgettext(message) if self._fallback else message

    def ngettext(self, msgid1, msgid2, n):
        if self._fallback:
            return self._fallback.ngettext(msgid1, msgid2, n)
        elif n == 1:
            return msgid1
        else:
            return msgid2

    def lngettext(self, msgid1, msgid2, n):
        if self._fallback:
            return self._fallback.lngettext(msgid1, msgid2, n)
        elif n == 1:
            return msgid1
        else:
            return msgid2

    def ugettext(self, message):
        return self._fallback.ugettext(message) if self._fallback else unicode(message)

    def ungettext(self, msgid1, msgid2, n):
        if self._fallback:
            return self._fallback.ungettext(msgid1, msgid2, n)
        elif n == 1:
            return unicode(msgid1)
        else:
            return unicode(msgid2)

    def info(self):
        return self._info

    def charset(self):
        return self._charset

    def output_charset(self):
        return self._output_charset

    def set_output_charset(self, charset):
        self._output_charset = charset

    def install(self, unicode=False, names=None):
        import __builtin__
        __builtin__.__dict__['_'] = unicode and self.ugettext or self.gettext
        if hasattr(names, '__contains__'):
            if 'gettext' in names:
                __builtin__.__dict__['gettext'] = __builtin__.__dict__['_']
            if 'ngettext' in names:
                __builtin__.__dict__['ngettext'] = unicode and self.ungettext or self.ngettext
            if 'lgettext' in names:
                __builtin__.__dict__['lgettext'] = self.lgettext
            if 'lngettext' in names:
                __builtin__.__dict__['lngettext'] = self.lngettext


class GNUTranslations(NullTranslations):
    LE_MAGIC = 2500072158L
    BE_MAGIC = 3725722773L

    def _parse(self, fp):
        unpack = struct.unpack
        filename = getattr(fp, 'name', '')
        self._catalog = catalog = {}
        self.plural = lambda n: int(n != 1)
        buf = fp.read()
        buflen = len(buf)
        magic = unpack('<I', buf[:4])[0]
        if magic == self.LE_MAGIC:
            version, msgcount, masteridx, transidx = unpack('<4I', buf[4:20])
            ii = '<II'
        elif magic == self.BE_MAGIC:
            version, msgcount, masteridx, transidx = unpack('>4I', buf[4:20])
            ii = '>II'
        else:
            raise IOError(0, 'Bad magic number', filename)
        for i in xrange(0, msgcount):
            mlen, moff = unpack(ii, buf[masteridx:masteridx + 8])
            mend = moff + mlen
            tlen, toff = unpack(ii, buf[transidx:transidx + 8])
            tend = toff + tlen
            if mend < buflen and tend < buflen:
                msg = buf[moff:mend]
                tmsg = buf[toff:tend]
            else:
                raise IOError(0, 'File is corrupt', filename)
            if mlen == 0:
                lastk = k = None
                for item in tmsg.splitlines():
                    item = item.strip()
                    if not item:
                        continue
                    if ':' in item:
                        k, v = item.split(':', 1)
                        k = k.strip().lower()
                        v = v.strip()
                        self._info[k] = v
                        lastk = k
                    elif lastk:
                        self._info[lastk] += '\n' + item
                    if k == 'content-type':
                        self._charset = v.split('charset=')[1]
                    if k == 'plural-forms':
                        v = v.split(';')
                        plural = v[1].split('plural=')[1]
                        self.plural = c2py(plural)

            if '\x00' in msg:
                msgid1, msgid2 = msg.split('\x00')
                tmsg = tmsg.split('\x00')
                if self._charset:
                    msgid1 = unicode(msgid1, self._charset)
                    tmsg = [ unicode(x, self._charset) for x in tmsg ]
                for i in range(len(tmsg)):
                    catalog[msgid1, i] = tmsg[i]

            else:
                if self._charset:
                    msg = unicode(msg, self._charset)
                    tmsg = unicode(tmsg, self._charset)
                catalog[msg] = tmsg
            masteridx += 8
            transidx += 8

        return

    def gettext(self, message):
        missing = object()
        tmsg = self._catalog.get(message, missing)
        if tmsg is missing:
            if self._fallback:
                return self._fallback.gettext(message)
            return message
        if self._output_charset:
            return tmsg.encode(self._output_charset)
        return tmsg.encode(self._charset) if self._charset else tmsg

    def lgettext(self, message):
        missing = object()
        tmsg = self._catalog.get(message, missing)
        if tmsg is missing:
            if self._fallback:
                return self._fallback.lgettext(message)
            return message
        return tmsg.encode(self._output_charset) if self._output_charset else tmsg.encode(locale.getpreferredencoding())

    def ngettext(self, msgid1, msgid2, n):
        try:
            tmsg = self._catalog[msgid1, self.plural(n)]
            if self._output_charset:
                return tmsg.encode(self._output_charset)
            if self._charset:
                return tmsg.encode(self._charset)
            return tmsg
        except KeyError:
            if self._fallback:
                return self._fallback.ngettext(msgid1, msgid2, n)
            elif n == 1:
                return msgid1
            else:
                return msgid2

    def lngettext(self, msgid1, msgid2, n):
        try:
            tmsg = self._catalog[msgid1, self.plural(n)]
            if self._output_charset:
                return tmsg.encode(self._output_charset)
            return tmsg.encode(locale.getpreferredencoding())
        except KeyError:
            if self._fallback:
                return self._fallback.lngettext(msgid1, msgid2, n)
            elif n == 1:
                return msgid1
            else:
                return msgid2

    def ugettext(self, message):
        missing = object()
        tmsg = self._catalog.get(message, missing)
        if tmsg is missing:
            if self._fallback:
                return self._fallback.ugettext(message)
            return unicode(message)
        return tmsg

    def ungettext(self, msgid1, msgid2, n):
        try:
            tmsg = self._catalog[msgid1, self.plural(n)]
        except KeyError:
            if self._fallback:
                return self._fallback.ungettext(msgid1, msgid2, n)
            if n == 1:
                tmsg = unicode(msgid1)
            else:
                tmsg = unicode(msgid2)

        return tmsg


def find(domain, localedir=None, languages=None, all=0):
    if localedir is None:
        localedir = _default_localedir
    if languages is None:
        languages = []
        for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            val = os.environ.get(envar)
            if val:
                languages = val.split(':')
                break

        if 'C' not in languages:
            languages.append('C')
    nelangs = []
    for lang in languages:
        for nelang in _expand_lang(lang):
            if nelang not in nelangs:
                nelangs.append(nelang)

    if all:
        result = []
    else:
        result = None
    for lang in nelangs:
        if lang == 'C':
            break
        mofile = os.path.join(localedir, lang, 'LC_MESSAGES', '%s.mo' % domain)
        if os.path.exists(mofile):
            if all:
                result.append(mofile)
            else:
                return mofile

    return result


_translations = {}

def translation(domain, localedir=None, languages=None, class_=None, fallback=False, codeset=None):
    if class_ is None:
        class_ = GNUTranslations
    mofiles = find(domain, localedir, languages, all=1)
    if not mofiles:
        if fallback:
            return NullTranslations()
        raise IOError(ENOENT, 'No translation file found for domain', domain)
    result = None
    for mofile in mofiles:
        key = (class_, os.path.abspath(mofile))
        t = _translations.get(key)
        if t is None:
            with open(mofile, 'rb') as fp:
                t = _translations.setdefault(key, class_(fp))
        t = copy.copy(t)
        if codeset:
            t.set_output_charset(codeset)
        if result is None:
            result = t
        result.add_fallback(t)

    return result


def install(domain, localedir=None, unicode=False, codeset=None, names=None):
    t = translation(domain, localedir, fallback=True, codeset=codeset)
    t.install(unicode, names)


_localedirs = {}
_localecodesets = {}
_current_domain = 'messages'

def textdomain(domain=None):
    global _current_domain
    if domain is not None:
        _current_domain = domain
    return _current_domain


def bindtextdomain(domain, localedir=None):
    global _localedirs
    if localedir is not None:
        _localedirs[domain] = localedir
    return _localedirs.get(domain, _default_localedir)


def bind_textdomain_codeset(domain, codeset=None):
    global _localecodesets
    if codeset is not None:
        _localecodesets[domain] = codeset
    return _localecodesets.get(domain)


def dgettext(domain, message):
    try:
        t = translation(domain, _localedirs.get(domain, None), codeset=_localecodesets.get(domain))
    except IOError:
        return message

    return t.gettext(message)


def ldgettext(domain, message):
    try:
        t = translation(domain, _localedirs.get(domain, None), codeset=_localecodesets.get(domain))
    except IOError:
        return message

    return t.lgettext(message)


def dngettext(domain, msgid1, msgid2, n):
    try:
        t = translation(domain, _localedirs.get(domain, None), codeset=_localecodesets.get(domain))
    except IOError:
        if n == 1:
            return msgid1
        else:
            return msgid2

    return t.ngettext(msgid1, msgid2, n)


def ldngettext(domain, msgid1, msgid2, n):
    try:
        t = translation(domain, _localedirs.get(domain, None), codeset=_localecodesets.get(domain))
    except IOError:
        if n == 1:
            return msgid1
        else:
            return msgid2

    return t.lngettext(msgid1, msgid2, n)


def gettext(message):
    return dgettext(_current_domain, message)


def lgettext(message):
    return ldgettext(_current_domain, message)


def ngettext(msgid1, msgid2, n):
    return dngettext(_current_domain, msgid1, msgid2, n)


def lngettext(msgid1, msgid2, n):
    return ldngettext(_current_domain, msgid1, msgid2, n)


Catalog = translation
