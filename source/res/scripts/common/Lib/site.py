# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/site.py
import sys
import os
import __builtin__
import traceback
PREFIXES = [sys.prefix, sys.exec_prefix]
ENABLE_USER_SITE = None
USER_SITE = None
USER_BASE = None

def makepath(*paths):
    dir = os.path.join(*paths)
    try:
        dir = os.path.abspath(dir)
    except OSError:
        pass

    return (dir, os.path.normcase(dir))


def abs__file__():
    for m in sys.modules.values():
        if hasattr(m, '__loader__'):
            continue
        try:
            m.__file__ = os.path.abspath(m.__file__)
        except (AttributeError, OSError):
            pass


def removeduppaths():
    L = []
    known_paths = set()
    for dir in sys.path:
        dir, dircase = makepath(dir)
        if dircase not in known_paths:
            L.append(dir)
            known_paths.add(dircase)

    sys.path[:] = L
    return known_paths


def _init_pathinfo():
    d = set()
    for dir in sys.path:
        try:
            if os.path.isdir(dir):
                dir, dircase = makepath(dir)
                d.add(dircase)
        except TypeError:
            continue

    return d


def addpackage(sitedir, name, known_paths):
    if known_paths is None:
        _init_pathinfo()
        reset = 1
    else:
        reset = 0
    fullname = os.path.join(sitedir, name)
    try:
        f = open(fullname, 'rU')
    except IOError:
        return

    with f:
        for n, line in enumerate(f):
            if line.startswith('#'):
                continue
            try:
                if line.startswith(('import ', 'import\t')):
                    exec line
                    continue
                line = line.rstrip()
                dir, dircase = makepath(sitedir, line)
                if dircase not in known_paths and os.path.exists(dir):
                    sys.path.append(dir)
                    known_paths.add(dircase)
            except Exception as err:
                print >> sys.stderr, 'Error processing line {:d} of {}:\n'.format(n + 1, fullname)
                for record in traceback.format_exception(*sys.exc_info()):
                    for line in record.splitlines():
                        print >> sys.stderr, '  ' + line

                print >> sys.stderr, '\nRemainder of file ignored'
                break

    if reset:
        known_paths = None
    return known_paths


def addsitedir(sitedir, known_paths=None):
    if known_paths is None:
        known_paths = _init_pathinfo()
        reset = 1
    else:
        reset = 0
    sitedir, sitedircase = makepath(sitedir)
    if sitedircase not in known_paths:
        sys.path.append(sitedir)
    try:
        names = os.listdir(sitedir)
    except os.error:
        return

    dotpth = os.extsep + 'pth'
    names = [ name for name in names if name.endswith(dotpth) ]
    for name in sorted(names):
        addpackage(sitedir, name, known_paths)

    if reset:
        known_paths = None
    return known_paths


def check_enableusersite():
    if sys.flags.no_user_site:
        return False
    else:
        if hasattr(os, 'getuid') and hasattr(os, 'geteuid'):
            if os.geteuid() != os.getuid():
                return None
        if hasattr(os, 'getgid') and hasattr(os, 'getegid'):
            if os.getegid() != os.getgid():
                return None
        return True


def getuserbase():
    global USER_BASE
    if USER_BASE is not None:
        return USER_BASE
    else:
        from sysconfig import get_config_var
        USER_BASE = get_config_var('userbase')
        return USER_BASE


def getusersitepackages():
    global USER_SITE
    user_base = getuserbase()
    if USER_SITE is not None:
        return USER_SITE
    else:
        from sysconfig import get_path
        import os
        if sys.platform == 'darwin':
            from sysconfig import get_config_var
            if get_config_var('PYTHONFRAMEWORK'):
                USER_SITE = get_path('purelib', 'osx_framework_user')
                return USER_SITE
        USER_SITE = get_path('purelib', '%s_user' % os.name)
        return USER_SITE


def addusersitepackages(known_paths):
    global ENABLE_USER_SITE
    user_site = getusersitepackages()
    if ENABLE_USER_SITE and os.path.isdir(user_site):
        addsitedir(user_site, known_paths)
    return known_paths


def getsitepackages():
    sitepackages = []
    seen = set()
    for prefix in PREFIXES:
        if not prefix or prefix in seen:
            continue
        seen.add(prefix)
        if sys.platform in ('os2emx', 'riscos'):
            sitepackages.append(os.path.join(prefix, 'Lib', 'site-packages'))
        if os.sep == '/':
            sitepackages.append(os.path.join(prefix, 'lib', 'python' + sys.version[:3], 'site-packages'))
            sitepackages.append(os.path.join(prefix, 'lib', 'site-python'))
        sitepackages.append(prefix)
        sitepackages.append(os.path.join(prefix, 'lib', 'site-packages'))

    return sitepackages


def addsitepackages(known_paths):
    for sitedir in getsitepackages():
        if os.path.isdir(sitedir):
            addsitedir(sitedir, known_paths)

    return known_paths


def setBEGINLIBPATH():
    dllpath = os.path.join(sys.prefix, 'Lib', 'lib-dynload')
    libpath = os.environ['BEGINLIBPATH'].split(';')
    if libpath[-1]:
        libpath.append(dllpath)
    else:
        libpath[-1] = dllpath
    os.environ['BEGINLIBPATH'] = ';'.join(libpath)


def setquit():
    if os.sep == ':':
        eof = 'Cmd-Q'
    elif os.sep == '\\':
        eof = 'Ctrl-Z plus Return'
    else:
        eof = 'Ctrl-D (i.e. EOF)'

    class Quitter(object):

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return 'Use %s() or %s to exit' % (self.name, eof)

        def __call__(self, code=None):
            try:
                sys.stdin.close()
            except:
                pass

            raise SystemExit(code)

    __builtin__.quit = Quitter('quit')
    __builtin__.exit = Quitter('exit')


class _Printer(object):
    MAXLINES = 23

    def __init__(self, name, data, files=(), dirs=()):
        self.__name = name
        self.__data = data
        self.__files = files
        self.__dirs = dirs
        self.__lines = None
        return

    def __setup(self):
        if self.__lines:
            return
        else:
            data = None
            for dir in self.__dirs:
                for filename in self.__files:
                    filename = os.path.join(dir, filename)
                    try:
                        fp = file(filename, 'rU')
                        data = fp.read()
                        fp.close()
                        break
                    except IOError:
                        pass

                if data:
                    break

            if not data:
                data = self.__data
            self.__lines = data.split('\n')
            self.__linecnt = len(self.__lines)
            return

    def __repr__(self):
        self.__setup()
        if len(self.__lines) <= self.MAXLINES:
            return '\n'.join(self.__lines)
        else:
            return 'Type %s() to see the full %s text' % ((self.__name,) * 2)

    def __call__(self):
        self.__setup()
        prompt = 'Hit Return for more, or q (and Return) to quit: '
        lineno = 0
        while 1:
            try:
                for i in range(lineno, lineno + self.MAXLINES):
                    print self.__lines[i]

            except IndexError:
                break
            else:
                lineno += self.MAXLINES
                key = None
                while key is None:
                    key = raw_input(prompt)
                    if key not in ('', 'q'):
                        key = None

                if key == 'q':
                    break

        return


def setcopyright():
    __builtin__.copyright = _Printer('copyright', sys.copyright)
    if sys.platform[:4] == 'java':
        __builtin__.credits = _Printer('credits', 'Jython is maintained by the Jython developers (www.jython.org).')
    else:
        __builtin__.credits = _Printer('credits', '    Thanks to CWI, CNRI, BeOpen.com, Zope Corporation and a cast of thousands\n    for supporting Python development.  See www.python.org for more information.')
    here = os.path.dirname(os.__file__)
    __builtin__.license = _Printer('license', 'See https://www.python.org/psf/license/', ['LICENSE.txt', 'LICENSE'], [os.path.join(here, os.pardir), here, os.curdir])


class _Helper(object):

    def __repr__(self):
        pass

    def __call__(self, *args, **kwds):
        import pydoc
        return pydoc.help(*args, **kwds)


def sethelper():
    __builtin__.help = _Helper()


def aliasmbcs():
    if sys.platform == 'win32':
        import locale, codecs
        enc = locale.getdefaultlocale()[1]
        if enc.startswith('cp'):
            try:
                codecs.lookup(enc)
            except LookupError:
                import encodings
                encodings._cache[enc] = encodings._unknown
                encodings.aliases.aliases[enc] = 'mbcs'


def setencoding():
    encoding = 'ascii'
    if encoding != 'ascii':
        sys.setdefaultencoding(encoding)


def execsitecustomize():
    try:
        import sitecustomize
    except ImportError:
        pass
    except Exception:
        if sys.flags.verbose:
            sys.excepthook(*sys.exc_info())
        else:
            print >> sys.stderr, "'import sitecustomize' failed; use -v for traceback"


def execusercustomize():
    try:
        import usercustomize
    except ImportError:
        pass
    except Exception:
        if sys.flags.verbose:
            sys.excepthook(*sys.exc_info())
        else:
            print >> sys.stderr, "'import usercustomize' failed; use -v for traceback"


def main():
    global ENABLE_USER_SITE
    abs__file__()
    known_paths = removeduppaths()
    if ENABLE_USER_SITE is None:
        ENABLE_USER_SITE = check_enableusersite()
    known_paths = addusersitepackages(known_paths)
    known_paths = addsitepackages(known_paths)
    if sys.platform == 'os2emx':
        setBEGINLIBPATH()
    setquit()
    setcopyright()
    sethelper()
    aliasmbcs()
    setencoding()
    execsitecustomize()
    if ENABLE_USER_SITE:
        execusercustomize()
    if hasattr(sys, 'setdefaultencoding'):
        del sys.setdefaultencoding
    return


main()

def _script():
    help = "    %s [--user-base] [--user-site]\n\n    Without arguments print some useful information\n    With arguments print the value of USER_BASE and/or USER_SITE separated\n    by '%s'.\n\n    Exit codes with --user-base or --user-site:\n      0 - user site directory is enabled\n      1 - user site directory is disabled by user\n      2 - uses site directory is disabled by super user\n          or for security reasons\n     >2 - unknown error\n    "
    args = sys.argv[1:]
    if not args:
        print 'sys.path = ['
        for dir in sys.path:
            print '    %r,' % (dir,)

        print ']'
        print 'USER_BASE: %r (%s)' % (USER_BASE, 'exists' if os.path.isdir(USER_BASE) else "doesn't exist")
        print 'USER_SITE: %r (%s)' % (USER_SITE, 'exists' if os.path.isdir(USER_SITE) else "doesn't exist")
        print 'ENABLE_USER_SITE: %r' % ENABLE_USER_SITE
        sys.exit(0)
    buffer = []
    if '--user-base' in args:
        buffer.append(USER_BASE)
    if '--user-site' in args:
        buffer.append(USER_SITE)
    if buffer:
        print os.pathsep.join(buffer)
        if ENABLE_USER_SITE:
            sys.exit(0)
        elif ENABLE_USER_SITE is False:
            sys.exit(1)
        elif ENABLE_USER_SITE is None:
            sys.exit(2)
        else:
            sys.exit(3)
    else:
        import textwrap
        print textwrap.dedent(help % (sys.argv[0], os.pathsep))
        sys.exit(10)
    return


if __name__ == '__main__':
    _script()
