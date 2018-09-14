# Embedded file name: scripts/common/Lib/plat-mac/bundlebuilder.py
"""bundlebuilder.py -- Tools to assemble MacOS X (application) bundles.

This module contains two classes to build so called "bundles" for
MacOS X. BundleBuilder is a general tool, AppBuilder is a subclass
specialized in building application bundles.

[Bundle|App]Builder objects are instantiated with a bunch of keyword
arguments, and have a build() method that will do all the work. See
the class doc strings for a description of the constructor arguments.

The module contains a main program that can be used in two ways:

  % python bundlebuilder.py [options] build
  % python buildapp.py [options] build

Where "buildapp.py" is a user-supplied setup.py-like script following
this model:

  from bundlebuilder import buildapp
  buildapp(<lots-of-keyword-args>)

"""
__all__ = ['BundleBuilder',
 'BundleBuilderError',
 'AppBuilder',
 'buildapp']
from warnings import warnpy3k
warnpy3k('In 3.x, the bundlebuilder module is removed.', stacklevel=2)
import sys
import os, errno, shutil
import imp, marshal
import re
from copy import deepcopy
import getopt
from plistlib import Plist
from types import FunctionType as function

class BundleBuilderError(Exception):
    pass


class Defaults():
    """Class attributes that don't start with an underscore and are
    not functions or classmethods are (deep)copied to self.__dict__.
    This allows for mutable default values.
    """

    def __init__(self, **kwargs):
        defaults = self._getDefaults()
        defaults.update(kwargs)
        self.__dict__.update(defaults)

    def _getDefaults(cls):
        defaults = {}
        for base in cls.__bases__:
            if hasattr(base, '_getDefaults'):
                defaults.update(base._getDefaults())

        for name, value in cls.__dict__.items():
            if name[0] != '_' and not isinstance(value, (function, classmethod)):
                defaults[name] = deepcopy(value)

        return defaults

    _getDefaults = classmethod(_getDefaults)


class BundleBuilder(Defaults):
    """BundleBuilder is a barebones class for assembling bundles. It
    knows nothing about executables or icons, it only copies files
    and creates the PkgInfo and Info.plist files.
    """
    name = None
    plist = Plist(CFBundleDevelopmentRegion='English', CFBundleInfoDictionaryVersion='6.0')
    type = 'BNDL'
    creator = None
    bundle_id = None
    resources = []
    files = []
    libs = []
    builddir = 'build'
    symlink = 0
    verbosity = 1
    destroot = ''

    def setup(self):
        self.name, ext = os.path.splitext(self.name)
        if not ext:
            ext = '.bundle'
        bundleextension = ext
        self.bundlepath = pathjoin(self.builddir, self.name + bundleextension)
        plist = self.plist
        plist.CFBundleName = self.name
        plist.CFBundlePackageType = self.type
        if self.creator is None:
            if hasattr(plist, 'CFBundleSignature'):
                self.creator = plist.CFBundleSignature
            else:
                self.creator = '????'
        plist.CFBundleSignature = self.creator
        if self.bundle_id:
            plist.CFBundleIdentifier = self.bundle_id
        elif not hasattr(plist, 'CFBundleIdentifier'):
            plist.CFBundleIdentifier = self.name
        return

    def build(self):
        """Build the bundle."""
        builddir = self.builddir
        if builddir and not os.path.exists(builddir):
            os.mkdir(builddir)
        self.message('Building %s' % repr(self.bundlepath), 1)
        if os.path.exists(self.bundlepath):
            shutil.rmtree(self.bundlepath)
        if os.path.exists(self.bundlepath + '~'):
            shutil.rmtree(self.bundlepath + '~')
        bp = self.bundlepath
        self.bundlepath = bp + '~'
        try:
            os.mkdir(self.bundlepath)
            self.preProcess()
            self._copyFiles()
            self._addMetaFiles()
            self.postProcess()
            os.rename(self.bundlepath, bp)
        finally:
            self.bundlepath = bp

        self.message('Done.', 1)

    def preProcess(self):
        """Hook for subclasses."""
        pass

    def postProcess(self):
        """Hook for subclasses."""
        pass

    def _addMetaFiles(self):
        contents = pathjoin(self.bundlepath, 'Contents')
        makedirs(contents)
        raise len(self.type) == len(self.creator) == 4 or AssertionError('type and creator must be 4-byte strings.')
        pkginfo = pathjoin(contents, 'PkgInfo')
        f = open(pkginfo, 'wb')
        f.write(self.type + self.creator)
        f.close()
        infoplist = pathjoin(contents, 'Info.plist')
        self.plist.write(infoplist)

    def _copyFiles(self):
        files = self.files[:]
        for path in self.resources:
            files.append((path, pathjoin('Contents', 'Resources', os.path.basename(path))))

        for path in self.libs:
            files.append((path, pathjoin('Contents', 'Frameworks', os.path.basename(path))))

        if self.symlink:
            self.message('Making symbolic links', 1)
            msg = 'Making symlink from'
        else:
            self.message('Copying files', 1)
            msg = 'Copying'
        files.sort()
        for src, dst in files:
            if os.path.isdir(src):
                self.message('%s %s/ to %s/' % (msg, src, dst), 2)
            else:
                self.message('%s %s to %s' % (msg, src, dst), 2)
            dst = pathjoin(self.bundlepath, dst)
            if self.symlink:
                symlink(src, dst, mkdirs=1)
            else:
                copy(src, dst, mkdirs=1)

    def message(self, msg, level = 0):
        if level <= self.verbosity:
            indent = ''
            if level > 1:
                indent = (level - 1) * '  '
            sys.stderr.write(indent + msg + '\n')

    def report(self):
        pass


PYC_EXT = '.pyc'
MAGIC = imp.get_magic()
USE_ZIPIMPORT = 'zipimport' in sys.builtin_module_names
SITE_PY = 'import sys\nif not %(semi_standalone)s:\n    del sys.path[1:]  # sys.path[0] is Contents/Resources/\n'
ZIP_ARCHIVE = 'Modules.zip'
SITE_PY_ZIP = SITE_PY + "sys.path.append(sys.path[0] + '/%s')\n" % ZIP_ARCHIVE

def getPycData(fullname, code, ispkg):
    if ispkg:
        fullname += '.__init__'
    path = fullname.replace('.', os.sep) + PYC_EXT
    return (path, MAGIC + '\x00\x00\x00\x00' + marshal.dumps(code))


EXT_LOADER = 'def __load():\n    import imp, sys, os\n    for p in sys.path:\n        path = os.path.join(p, "%(filename)s")\n        if os.path.exists(path):\n            break\n    else:\n        assert 0, "file not found: %(filename)s"\n    mod = imp.load_dynamic("%(name)s", path)\n\n__load()\ndel __load\n'
MAYMISS_MODULES = ['os2',
 'nt',
 'ntpath',
 'dos',
 'dospath',
 'win32api',
 'ce',
 '_winreg',
 'nturl2path',
 'sitecustomize',
 'org.python.core',
 'riscos',
 'riscosenviron',
 'riscospath']
STRIP_EXEC = '/usr/bin/strip'
BOOTSTRAP_SCRIPT = '#!%(hashbang)s\n\nimport sys, os\nexecdir = os.path.dirname(sys.argv[0])\nexecutable = os.path.join(execdir, "%(executable)s")\nresdir = os.path.join(os.path.dirname(execdir), "Resources")\nlibdir = os.path.join(os.path.dirname(execdir), "Frameworks")\nmainprogram = os.path.join(resdir, "%(mainprogram)s")\n\nif %(optimize)s:\n    sys.argv.insert(1, \'-O\')\n\nsys.argv.insert(1, mainprogram)\nif %(standalone)s or %(semi_standalone)s:\n    os.environ["PYTHONPATH"] = resdir\n    if %(standalone)s:\n        os.environ["PYTHONHOME"] = resdir\nelse:\n    pypath = os.getenv("PYTHONPATH", "")\n    if pypath:\n        pypath = ":" + pypath\n    os.environ["PYTHONPATH"] = resdir + pypath\n\nos.environ["PYTHONEXECUTABLE"] = executable\nos.environ["DYLD_LIBRARY_PATH"] = libdir\nos.environ["DYLD_FRAMEWORK_PATH"] = libdir\nos.execve(executable, sys.argv, os.environ)\n'
ARGV_EMULATOR = 'import argvemulator, os\n\nargvemulator.ArgvCollector().mainloop()\nexecfile(os.path.join(os.path.split(__file__)[0], "%(realmainprogram)s"))\n'
PYTHONFRAMEWORKGOODIES = ['Python', 'Resources/English.lproj', 'Resources/Info.plist']

def isFramework():
    return sys.exec_prefix.find('Python.framework') > 0


LIB = os.path.join(sys.prefix, 'lib', 'python' + sys.version[:3])
SITE_PACKAGES = os.path.join(LIB, 'site-packages')

class AppBuilder(BundleBuilder):
    use_zipimport = USE_ZIPIMPORT
    type = 'APPL'
    platform = 'MacOS'
    mainprogram = None
    executable = None
    nibname = None
    iconfile = None
    symlink_exec = 0
    standalone = 0
    semi_standalone = 0
    python = None
    argv_emulation = 0
    excludeModules = []
    includeModules = []
    includePackages = []
    strip = 0
    pymodules = []
    missingModules = []
    maybeMissingModules = []

    def setup(self):
        if (self.standalone or self.semi_standalone) and self.mainprogram is None:
            raise BundleBuilderError, "must specify 'mainprogram' when building a standalone application."
        if self.mainprogram is None and self.executable is None:
            raise BundleBuilderError, "must specify either or both of 'executable' and 'mainprogram'"
        self.execdir = pathjoin('Contents', self.platform)
        if self.name is not None:
            pass
        elif self.mainprogram is not None:
            self.name = os.path.splitext(os.path.basename(self.mainprogram))[0]
        elif self.executable is not None:
            self.name = os.path.splitext(os.path.basename(self.executable))[0]
        if self.name[-4:] != '.app':
            self.name += '.app'
        if self.executable is None:
            if not self.standalone and not isFramework():
                self.symlink_exec = 1
            if self.python:
                self.executable = self.python
            else:
                self.executable = sys.executable
        if self.nibname:
            self.plist.NSMainNibFile = self.nibname
            if not hasattr(self.plist, 'NSPrincipalClass'):
                self.plist.NSPrincipalClass = 'NSApplication'
        if self.standalone and isFramework():
            self.addPythonFramework()
        BundleBuilder.setup(self)
        self.plist.CFBundleExecutable = self.name
        if self.standalone or self.semi_standalone:
            self.findDependencies()
        return

    def preProcess(self):
        resdir = 'Contents/Resources'
        if self.executable is not None:
            if self.mainprogram is None:
                execname = self.name
            else:
                execname = os.path.basename(self.executable)
            execpath = pathjoin(self.execdir, execname)
            if not self.symlink_exec:
                self.files.append((self.destroot + self.executable, execpath))
            self.execpath = execpath
        if self.mainprogram is not None:
            mainprogram = os.path.basename(self.mainprogram)
            self.files.append((self.mainprogram, pathjoin(resdir, mainprogram)))
            if self.argv_emulation:
                realmainprogram = mainprogram
                mainprogram = '__argvemulator_' + mainprogram
                resdirpath = pathjoin(self.bundlepath, resdir)
                mainprogrampath = pathjoin(resdirpath, mainprogram)
                makedirs(resdirpath)
                open(mainprogrampath, 'w').write(ARGV_EMULATOR % locals())
                if self.standalone or self.semi_standalone:
                    self.includeModules.append('argvemulator')
                    self.includeModules.append('os')
                if 'CFBundleDocumentTypes' not in self.plist:
                    self.plist['CFBundleDocumentTypes'] = [{'CFBundleTypeOSTypes': ['****', 'fold', 'disk'],
                      'CFBundleTypeRole': 'Viewer'}]
            executable = os.path.basename(self.executable)
            execdir = pathjoin(self.bundlepath, self.execdir)
            bootstrappath = pathjoin(execdir, self.name)
            makedirs(execdir)
            if self.standalone or self.semi_standalone:
                hashbang = '/usr/bin/python'
            elif self.python:
                hashbang = self.python
            else:
                hashbang = os.path.realpath(sys.executable)
            standalone = self.standalone
            semi_standalone = self.semi_standalone
            optimize = sys.flags.optimize
            open(bootstrappath, 'w').write(BOOTSTRAP_SCRIPT % locals())
            os.chmod(bootstrappath, 509)
        if self.iconfile is not None:
            iconbase = os.path.basename(self.iconfile)
            self.plist.CFBundleIconFile = iconbase
            self.files.append((self.iconfile, pathjoin(resdir, iconbase)))
        return

    def postProcess(self):
        if self.standalone or self.semi_standalone:
            self.addPythonModules()
        if self.strip and not self.symlink:
            self.stripBinaries()
        if self.symlink_exec and self.executable:
            self.message('Symlinking executable %s to %s' % (self.executable, self.execpath), 2)
            dst = pathjoin(self.bundlepath, self.execpath)
            makedirs(os.path.dirname(dst))
            os.symlink(os.path.abspath(self.executable), dst)
        if self.missingModules or self.maybeMissingModules:
            self.reportMissing()

    def addPythonFramework(self):
        for lib in self.libs:
            if os.path.basename(lib) == 'Python.framework':
                return

        frameworkpath = sys.exec_prefix[:sys.exec_prefix.find('Python.framework') + len('Python.framework')]
        version = sys.version[:3]
        frameworkpath = pathjoin(frameworkpath, 'Versions', version)
        destbase = pathjoin('Contents', 'Frameworks', 'Python.framework', 'Versions', version)
        for item in PYTHONFRAMEWORKGOODIES:
            src = pathjoin(frameworkpath, item)
            dst = pathjoin(destbase, item)
            self.files.append((src, dst))

    def _getSiteCode(self):
        if self.use_zipimport:
            return compile(SITE_PY % {'semi_standalone': self.semi_standalone}, '<-bundlebuilder.py->', 'exec')

    def addPythonModules(self):
        self.message('Adding Python modules', 1)
        if self.use_zipimport:
            import zipfile
            relpath = pathjoin('Contents', 'Resources', ZIP_ARCHIVE)
            abspath = pathjoin(self.bundlepath, relpath)
            zf = zipfile.ZipFile(abspath, 'w', zipfile.ZIP_DEFLATED)
            for name, code, ispkg in self.pymodules:
                self.message('Adding Python module %s' % name, 2)
                path, pyc = getPycData(name, code, ispkg)
                zf.writestr(path, pyc)

            zf.close()
            sitepath = pathjoin(self.bundlepath, 'Contents', 'Resources', 'site' + PYC_EXT)
            writePyc(self._getSiteCode(), sitepath)
        else:
            for name, code, ispkg in self.pymodules:
                if ispkg:
                    name += '.__init__'
                path = name.split('.')
                path = pathjoin('Contents', 'Resources', *path) + PYC_EXT
                if ispkg:
                    self.message('Adding Python package %s' % path, 2)
                else:
                    self.message('Adding Python module %s' % path, 2)
                abspath = pathjoin(self.bundlepath, path)
                makedirs(os.path.dirname(abspath))
                writePyc(code, abspath)

    def stripBinaries(self):
        if not os.path.exists(STRIP_EXEC):
            self.message("Error: can't strip binaries: no strip program at %s" % STRIP_EXEC, 0)
        else:
            import stat
            self.message('Stripping binaries', 1)

            def walk(top):
                for name in os.listdir(top):
                    path = pathjoin(top, name)
                    if os.path.islink(path):
                        continue
                    if os.path.isdir(path):
                        walk(path)
                    else:
                        mod = os.stat(path)[stat.ST_MODE]
                        if not mod & 64:
                            continue
                        relpath = path[len(self.bundlepath):]
                        self.message('Stripping %s' % relpath, 2)
                        inf, outf = os.popen4('%s -S "%s"' % (STRIP_EXEC, path))
                        output = outf.read().strip()
                        if output:
                            self.message('Problem stripping %s:' % relpath, 3)
                            self.message(output, 3)

            walk(self.bundlepath)

    def findDependencies(self):
        self.message('Finding module dependencies', 1)
        import modulefinder
        mf = modulefinder.ModuleFinder(excludes=self.excludeModules)
        if self.use_zipimport:
            mf.import_hook('zlib')
        site = mf.add_module('site')
        site.__code__ = self._getSiteCode()
        mf.scan_code(site.__code__, site)
        mf.import_hook('warnings')
        includeModules = self.includeModules[:]
        for name in self.includePackages:
            includeModules.extend(findPackageContents(name).keys())

        for name in includeModules:
            try:
                mf.import_hook(name)
            except ImportError:
                self.missingModules.append(name)

        mf.run_script(self.mainprogram)
        modules = mf.modules.items()
        modules.sort()
        for name, mod in modules:
            path = mod.__file__
            if path and self.semi_standalone:
                if path.startswith(LIB) and not path.startswith(SITE_PACKAGES):
                    continue
            if path and mod.__code__ is None:
                filename = os.path.basename(path)
                pathitems = name.split('.')[:-1] + [filename]
                dstpath = pathjoin(*pathitems)
                if self.use_zipimport:
                    if name != 'zlib':
                        dstpath = pathjoin('ExtensionModules', dstpath)
                    source = EXT_LOADER % {'name': name,
                     'filename': dstpath}
                    code = compile(source, '<dynloader for %s>' % name, 'exec')
                    mod.__code__ = code
                self.files.append((path, pathjoin('Contents', 'Resources', dstpath)))
            if mod.__code__ is not None:
                ispkg = mod.__path__ is not None
                if not self.use_zipimport or name != 'site':
                    self.pymodules.append((name, mod.__code__, ispkg))

        if hasattr(mf, 'any_missing_maybe'):
            missing, maybe = mf.any_missing_maybe()
        else:
            missing = mf.any_missing()
            maybe = []
        self.missingModules.extend(missing)
        self.maybeMissingModules.extend(maybe)
        return

    def reportMissing(self):
        missing = [ name for name in self.missingModules if name not in MAYMISS_MODULES ]
        if self.maybeMissingModules:
            maybe = self.maybeMissingModules
        else:
            maybe = [ name for name in missing if '.' in name ]
            missing = [ name for name in missing if '.' not in name ]
        missing.sort()
        maybe.sort()
        if maybe:
            self.message("Warning: couldn't find the following submodules:", 1)
            self.message("    (Note that these could be false alarms -- it's not always", 1)
            self.message('    possible to distinguish between "from package import submodule" ', 1)
            self.message('    and "from package import name")', 1)
            for name in maybe:
                self.message('  ? ' + name, 1)

        if missing:
            self.message("Warning: couldn't find the following modules:", 1)
            for name in missing:
                self.message('  ? ' + name, 1)

    def report(self):
        import pprint
        pprint.pprint(self.__dict__)
        if self.standalone or self.semi_standalone:
            self.reportMissing()


SUFFIXES = [ _suf for _suf, _mode, _tp in imp.get_suffixes() ]
identifierRE = re.compile('[_a-zA-z][_a-zA-Z0-9]*$')

def findPackageContents(name, searchpath = None):
    head = name.split('.')[-1]
    if identifierRE.match(head) is None:
        return {}
    else:
        try:
            fp, path, (ext, mode, tp) = imp.find_module(head, searchpath)
        except ImportError:
            return {}

        modules = {name: None}
        if tp == imp.PKG_DIRECTORY and path:
            files = os.listdir(path)
            for sub in files:
                sub, ext = os.path.splitext(sub)
                fullname = name + '.' + sub
                if sub != '__init__' and fullname not in modules:
                    modules.update(findPackageContents(fullname, [path]))

        return modules


def writePyc(code, path):
    f = open(path, 'wb')
    f.write(MAGIC)
    f.write('\x00\x00\x00\x00')
    marshal.dump(code, f)
    f.close()


def copy(src, dst, mkdirs = 0):
    """Copy a file or a directory."""
    if mkdirs:
        makedirs(os.path.dirname(dst))
    if os.path.isdir(src):
        shutil.copytree(src, dst, symlinks=1)
    else:
        shutil.copy2(src, dst)


def copytodir(src, dstdir):
    """Copy a file or a directory to an existing directory."""
    dst = pathjoin(dstdir, os.path.basename(src))
    copy(src, dst)


def makedirs(dir):
    """Make all directories leading up to 'dir' including the leaf
    directory. Don't moan if any path element already exists."""
    try:
        os.makedirs(dir)
    except OSError as why:
        if why.errno != errno.EEXIST:
            raise


def symlink(src, dst, mkdirs = 0):
    """Copy a file or a directory."""
    if not os.path.exists(src):
        raise IOError, "No such file or directory: '%s'" % src
    if mkdirs:
        makedirs(os.path.dirname(dst))
    os.symlink(os.path.abspath(src), dst)


def pathjoin(*args):
    """Safe wrapper for os.path.join: asserts that all but the first
    argument are relative paths."""
    for seg in args[1:]:
        raise seg[0] != '/' or AssertionError

    return os.path.join(*args)


cmdline_doc = 'Usage:\n  python bundlebuilder.py [options] command\n  python mybuildscript.py [options] command\n\nCommands:\n  build      build the application\n  report     print a report\n\nOptions:\n  -b, --builddir=DIR     the build directory; defaults to "build"\n  -n, --name=NAME        application name\n  -r, --resource=FILE    extra file or folder to be copied to Resources\n  -f, --file=SRC:DST     extra file or folder to be copied into the bundle;\n                         DST must be a path relative to the bundle root\n  -e, --executable=FILE  the executable to be used\n  -m, --mainprogram=FILE the Python main program\n  -a, --argv             add a wrapper main program to create sys.argv\n  -p, --plist=FILE       .plist file (default: generate one)\n      --nib=NAME         main nib name\n  -c, --creator=CCCC     4-char creator code (default: \'????\')\n      --iconfile=FILE    filename of the icon (an .icns file) to be used\n                         as the Finder icon\n      --bundle-id=ID     the CFBundleIdentifier, in reverse-dns format\n                         (eg. org.python.BuildApplet; this is used for\n                         the preferences file name)\n  -l, --link             symlink files/folder instead of copying them\n      --link-exec        symlink the executable instead of copying it\n      --standalone       build a standalone application, which is fully\n                         independent of a Python installation\n      --semi-standalone  build a standalone application, which depends on\n                         an installed Python, yet includes all third-party\n                         modules.\n      --no-zipimport     Do not copy code into a zip file\n      --python=FILE      Python to use in #! line in stead of current Python\n      --lib=FILE         shared library or framework to be copied into\n                         the bundle\n  -x, --exclude=MODULE   exclude module (with --(semi-)standalone)\n  -i, --include=MODULE   include module (with --(semi-)standalone)\n      --package=PACKAGE  include a whole package (with --(semi-)standalone)\n      --strip            strip binaries (remove debug info)\n  -v, --verbose          increase verbosity level\n  -q, --quiet            decrease verbosity level\n  -h, --help             print this message\n'

def usage(msg = None):
    if msg:
        print msg
    print cmdline_doc
    sys.exit(1)


def main(builder = None):
    if builder is None:
        builder = AppBuilder(verbosity=1)
    shortopts = 'b:n:r:f:e:m:c:p:lx:i:hvqa'
    longopts = ('builddir=', 'name=', 'resource=', 'file=', 'executable=', 'mainprogram=', 'creator=', 'nib=', 'plist=', 'link', 'link-exec', 'help', 'verbose', 'quiet', 'argv', 'standalone', 'exclude=', 'include=', 'package=', 'strip', 'iconfile=', 'lib=', 'python=', 'semi-standalone', 'bundle-id=', 'destroot=no-zipimport')
    try:
        options, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.error:
        usage()

    for opt, arg in options:
        if opt in ('-b', '--builddir'):
            builder.builddir = arg
        elif opt in ('-n', '--name'):
            builder.name = arg
        elif opt in ('-r', '--resource'):
            builder.resources.append(os.path.normpath(arg))
        elif opt in ('-f', '--file'):
            srcdst = arg.split(':')
            if len(srcdst) != 2:
                usage('-f or --file argument must be two paths, separated by a colon')
            builder.files.append(srcdst)
        elif opt in ('-e', '--executable'):
            builder.executable = arg
        elif opt in ('-m', '--mainprogram'):
            builder.mainprogram = arg
        elif opt in ('-a', '--argv'):
            builder.argv_emulation = 1
        elif opt in ('-c', '--creator'):
            builder.creator = arg
        elif opt == '--bundle-id':
            builder.bundle_id = arg
        elif opt == '--iconfile':
            builder.iconfile = arg
        elif opt == '--lib':
            builder.libs.append(os.path.normpath(arg))
        elif opt == '--nib':
            builder.nibname = arg
        elif opt in ('-p', '--plist'):
            builder.plist = Plist.fromFile(arg)
        elif opt in ('-l', '--link'):
            builder.symlink = 1
        elif opt == '--link-exec':
            builder.symlink_exec = 1
        elif opt in ('-h', '--help'):
            usage()
        elif opt in ('-v', '--verbose'):
            builder.verbosity += 1
        elif opt in ('-q', '--quiet'):
            builder.verbosity -= 1
        elif opt == '--standalone':
            builder.standalone = 1
        elif opt == '--semi-standalone':
            builder.semi_standalone = 1
        elif opt == '--python':
            builder.python = arg
        elif opt in ('-x', '--exclude'):
            builder.excludeModules.append(arg)
        elif opt in ('-i', '--include'):
            builder.includeModules.append(arg)
        elif opt == '--package':
            builder.includePackages.append(arg)
        elif opt == '--strip':
            builder.strip = 1
        elif opt == '--destroot':
            builder.destroot = arg
        elif opt == '--no-zipimport':
            builder.use_zipimport = False

    if len(args) != 1:
        usage("Must specify one command ('build', 'report' or 'help')")
    command = args[0]
    if command == 'build':
        builder.setup()
        builder.build()
    elif command == 'report':
        builder.setup()
        builder.report()
    elif command == 'help':
        usage()
    else:
        usage("Unknown command '%s'" % command)
    return


def buildapp(**kwargs):
    builder = AppBuilder(**kwargs)
    main(builder)


if __name__ == '__main__':
    main()
