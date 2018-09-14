# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bw_site.py
DEFAULT_ENCODING = 'utf-8'
import BWLogging
BWLogging.init()
import BigWorld
if BigWorld.component not in ('process_defs', 'client'):
    import BWUtil
    BWUtil.monkeyPatchOpen()
    import threading
    orig_bootstrap = threading.Thread._Thread__bootstrap

    def hooked_bootstrap(self):
        BigWorld.__onThreadStart(self.name)
        orig_bootstrap(self)
        BigWorld.__onThreadEnd()


    threading.Thread._Thread__bootstrap = hooked_bootstrap
import __builtin__
import pydoc

class _Helper(object):
    """Define the built-in 'help'.
    This is a wrapper around pydoc.help (with a twist).
    
    """

    def __repr__(self):
        pass

    def __call__(self, *args, **kwds):
        return pydoc.help(*args, **kwds)


def sethelper():
    __builtin__.help = _Helper()


import encodings
import sys

def setDefaultEncoding():
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding(DEFAULT_ENCODING)
        del sys.setdefaultencoding
        import logging
        configLog = logging.getLogger('Config')
        configLog.info('Default encoding set to %s', sys.getdefaultencoding())


import os
import traceback

def makepath(*paths):
    dir = os.path.join(*paths)
    try:
        dir = os.path.abspath(dir)
    except OSError:
        pass

    return (dir, os.path.normcase(dir))


def removeduppaths():
    """ Remove duplicate entries from sys.path along with making them
    absolute"""
    L = []
    known_paths = set()
    for dir in sys.path:
        dir, dircase = makepath(dir)
        if dircase not in known_paths:
            L.append(dir)
            known_paths.add(dircase)

    sys.path[:] = L
    return known_paths


def getsitepackages():
    """Returns a list containing all global site-packages directories
    (and possibly site-python).
    
    For each directory present in the global ``PREFIXES``, this function
    will find its `site-packages` subdirectory depending on the system
    environment, and will return a list of full paths.
    """
    sitepackages = []
    seen = set()
    for prefix in sys.path:
        if not prefix or prefix in seen:
            continue
        seen.add(prefix)
        sitepackages.append(os.path.join(prefix, 'site-packages'))

    return sitepackages


def _init_pathinfo():
    """Return a set containing all existing directory entries from sys.path"""
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
    """Process a .pth file within the site-packages directory:
       For each line in the file, either combine it with sitedir to a path
       and add that to known_paths, or execute it if it starts with 'import '.
    """
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


def addsitedir(sitedir, known_paths = None):
    """Add 'sitedir' argument to sys.path if missing and handle .pth files in
    'sitedir'"""
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


def addsitepackages(known_paths):
    """Add site-packages (and possibly site-python) to sys.path"""
    for sitedir in getsitepackages():
        if os.path.isdir(sitedir):
            addsitedir(sitedir, known_paths)

    return known_paths


def setUpPaths():
    known_paths = removeduppaths()
    known_paths = addsitepackages(known_paths)


def main():
    sethelper()
    setDefaultEncoding()
    if BigWorld.component not in ('client', 'bot'):
        setUpPaths()
    import bwpydevd
    bwpydevd.startDebug(isStartUp=True)


main()
import bwdeprecations
from bwdebug import NOTICE_MSG
try:
    import BWAutoImport
except ImportError as e:
    NOTICE_MSG('bw_site.py failed to import BWAutoImport: %s\n' % (e,))

try:
    import BWTwistedReactor
    import twisted.internet.selectreactor
    twisted.internet.selectreactor = BWTwistedReactor
except:
    pass
