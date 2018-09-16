# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/_MozillaCookieJar.py
import re, time
from cookielib import _warn_unhandled_exception, FileCookieJar, LoadError, Cookie, MISSING_FILENAME_TEXT

class MozillaCookieJar(FileCookieJar):
    magic_re = '#( Netscape)? HTTP Cookie File'
    header = '# Netscape HTTP Cookie File\n# http://curl.haxx.se/rfc/cookie_spec.html\n# This is a generated file!  Do not edit.\n\n'

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()
        magic = f.readline()
        if not re.search(self.magic_re, magic):
            f.close()
            raise LoadError('%r does not look like a Netscape format cookies file' % filename)
        try:
            while 1:
                line = f.readline()
                if line == '':
                    break
                if line.endswith('\n'):
                    line = line[:-1]
                if line.strip().startswith(('#', '$')) or line.strip() == '':
                    continue
                domain, domain_specified, path, secure, expires, name, value = line.split('\t')
                secure = secure == 'TRUE'
                domain_specified = domain_specified == 'TRUE'
                if name == '':
                    name = value
                    value = None
                initial_dot = domain.startswith('.')
                discard = False
                if expires == '':
                    expires = None
                    discard = True
                c = Cookie(0, name, value, None, False, domain, domain_specified, initial_dot, path, False, secure, expires, discard, None, None, {})
                if not ignore_discard and c.discard:
                    continue
                if not ignore_expires and c.is_expired(now):
                    continue
                self.set_cookie(c)

        except IOError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError('invalid Netscape format cookies file %r: %r' % (filename, line))

        return

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError(MISSING_FILENAME_TEXT)
        f = open(filename, 'w')
        try:
            f.write(self.header)
            now = time.time()
            for cookie in self:
                if not ignore_discard and cookie.discard:
                    continue
                if not ignore_expires and cookie.is_expired(now):
                    continue
                if cookie.secure:
                    secure = 'TRUE'
                else:
                    secure = 'FALSE'
                if cookie.domain.startswith('.'):
                    initial_dot = 'TRUE'
                else:
                    initial_dot = 'FALSE'
                if cookie.expires is not None:
                    expires = str(cookie.expires)
                else:
                    expires = ''
                if cookie.value is None:
                    name = ''
                    value = cookie.name
                else:
                    name = cookie.name
                    value = cookie.value
                f.write('\t'.join([cookie.domain,
                 initial_dot,
                 cookie.path,
                 secure,
                 expires,
                 name,
                 value]) + '\n')

        finally:
            f.close()

        return
