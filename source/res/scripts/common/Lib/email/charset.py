# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/email/charset.py
__all__ = ['Charset',
 'add_alias',
 'add_charset',
 'add_codec']
import codecs
import email.base64mime
import email.quoprimime
from email import errors
from email.encoders import encode_7or8bit
QP = 1
BASE64 = 2
SHORTEST = 3
MISC_LEN = 7
DEFAULT_CHARSET = 'us-ascii'
CHARSETS = {'iso-8859-1': (QP, QP, None),
 'iso-8859-2': (QP, QP, None),
 'iso-8859-3': (QP, QP, None),
 'iso-8859-4': (QP, QP, None),
 'iso-8859-9': (QP, QP, None),
 'iso-8859-10': (QP, QP, None),
 'iso-8859-13': (QP, QP, None),
 'iso-8859-14': (QP, QP, None),
 'iso-8859-15': (QP, QP, None),
 'iso-8859-16': (QP, QP, None),
 'windows-1252': (QP, QP, None),
 'viscii': (QP, QP, None),
 'us-ascii': (None, None, None),
 'big5': (BASE64, BASE64, None),
 'gb2312': (BASE64, BASE64, None),
 'euc-jp': (BASE64, None, 'iso-2022-jp'),
 'shift_jis': (BASE64, None, 'iso-2022-jp'),
 'iso-2022-jp': (BASE64, None, None),
 'koi8-r': (BASE64, BASE64, None),
 'utf-8': (SHORTEST, BASE64, 'utf-8'),
 '8bit': (None, BASE64, 'utf-8')}
ALIASES = {'latin_1': 'iso-8859-1',
 'latin-1': 'iso-8859-1',
 'latin_2': 'iso-8859-2',
 'latin-2': 'iso-8859-2',
 'latin_3': 'iso-8859-3',
 'latin-3': 'iso-8859-3',
 'latin_4': 'iso-8859-4',
 'latin-4': 'iso-8859-4',
 'latin_5': 'iso-8859-9',
 'latin-5': 'iso-8859-9',
 'latin_6': 'iso-8859-10',
 'latin-6': 'iso-8859-10',
 'latin_7': 'iso-8859-13',
 'latin-7': 'iso-8859-13',
 'latin_8': 'iso-8859-14',
 'latin-8': 'iso-8859-14',
 'latin_9': 'iso-8859-15',
 'latin-9': 'iso-8859-15',
 'latin_10': 'iso-8859-16',
 'latin-10': 'iso-8859-16',
 'cp949': 'ks_c_5601-1987',
 'euc_jp': 'euc-jp',
 'euc_kr': 'euc-kr',
 'ascii': 'us-ascii'}
CODEC_MAP = {'gb2312': 'eucgb2312_cn',
 'big5': 'big5_tw',
 'us-ascii': None}

def add_charset(charset, header_enc=None, body_enc=None, output_charset=None):
    if body_enc == SHORTEST:
        raise ValueError('SHORTEST not allowed for body_enc')
    CHARSETS[charset] = (header_enc, body_enc, output_charset)


def add_alias(alias, canonical):
    ALIASES[alias] = canonical


def add_codec(charset, codecname):
    CODEC_MAP[charset] = codecname


class Charset:

    def __init__(self, input_charset=DEFAULT_CHARSET):
        try:
            if isinstance(input_charset, unicode):
                input_charset.encode('ascii')
            else:
                input_charset = unicode(input_charset, 'ascii')
        except UnicodeError:
            raise errors.CharsetError(input_charset)

        input_charset = input_charset.lower().encode('ascii')
        if not (input_charset in ALIASES or input_charset in CHARSETS):
            try:
                input_charset = codecs.lookup(input_charset).name
            except LookupError:
                pass

        self.input_charset = ALIASES.get(input_charset, input_charset)
        henc, benc, conv = CHARSETS.get(self.input_charset, (SHORTEST, BASE64, None))
        if not conv:
            conv = self.input_charset
        self.header_encoding = henc
        self.body_encoding = benc
        self.output_charset = ALIASES.get(conv, conv)
        self.input_codec = CODEC_MAP.get(self.input_charset, self.input_charset)
        self.output_codec = CODEC_MAP.get(self.output_charset, self.output_charset)
        return

    def __str__(self):
        return self.input_charset.lower()

    __repr__ = __str__

    def __eq__(self, other):
        return str(self) == str(other).lower()

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_body_encoding(self):
        if self.body_encoding == QP:
            return 'quoted-printable'
        elif self.body_encoding == BASE64:
            return 'base64'
        else:
            return encode_7or8bit

    def convert(self, s):
        if self.input_codec != self.output_codec:
            return unicode(s, self.input_codec).encode(self.output_codec)
        else:
            return s

    def to_splittable(self, s):
        if isinstance(s, unicode) or self.input_codec is None:
            return s
        else:
            try:
                return unicode(s, self.input_codec, 'replace')
            except LookupError:
                return s

            return

    def from_splittable(self, ustr, to_output=True):
        if to_output:
            codec = self.output_codec
        else:
            codec = self.input_codec
        if not isinstance(ustr, unicode) or codec is None:
            return ustr
        else:
            try:
                return ustr.encode(codec, 'replace')
            except LookupError:
                return ustr

            return

    def get_output_charset(self):
        return self.output_charset or self.input_charset

    def encoded_header_len(self, s):
        cset = self.get_output_charset()
        if self.header_encoding == BASE64:
            return email.base64mime.base64_len(s) + len(cset) + MISC_LEN
        elif self.header_encoding == QP:
            return email.quoprimime.header_quopri_len(s) + len(cset) + MISC_LEN
        elif self.header_encoding == SHORTEST:
            lenb64 = email.base64mime.base64_len(s)
            lenqp = email.quoprimime.header_quopri_len(s)
            return min(lenb64, lenqp) + len(cset) + MISC_LEN
        else:
            return len(s)

    def header_encode(self, s, convert=False):
        cset = self.get_output_charset()
        if convert:
            s = self.convert(s)
        if self.header_encoding == BASE64:
            return email.base64mime.header_encode(s, cset)
        elif self.header_encoding == QP:
            return email.quoprimime.header_encode(s, cset, maxlinelen=None)
        else:
            if self.header_encoding == SHORTEST:
                lenb64 = email.base64mime.base64_len(s)
                lenqp = email.quoprimime.header_quopri_len(s)
                if lenb64 < lenqp:
                    return email.base64mime.header_encode(s, cset)
                else:
                    return email.quoprimime.header_encode(s, cset, maxlinelen=None)
            else:
                return s
            return None

    def body_encode(self, s, convert=True):
        if convert:
            s = self.convert(s)
        if self.body_encoding is BASE64:
            return email.base64mime.body_encode(s)
        elif self.body_encoding is QP:
            return email.quoprimime.body_encode(s)
        else:
            return s
