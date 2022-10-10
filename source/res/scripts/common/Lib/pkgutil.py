# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/pkgutil.py
import os
import sys
import imp
import os.path
from types import ModuleType
__all__ = ['get_importer',
 'iter_importers',
 'get_loader',
 'find_loader',
 'walk_packages',
 'iter_modules',
 'get_data',
 'ImpImporter',
 'ImpLoader',
 'read_code',
 'extend_path']

def read_code(stream):
    import marshal
    magic = stream.read(4)
    if magic != imp.get_magic():
        return
    else:
        stream.read(4)
        return marshal.load(stream)


def simplegeneric(func):
    registry = {}

    def wrapper(*args, **kw):
        ob = args[0]
        try:
            cls = ob.__class__
        except AttributeError:
            cls = type(ob)

        try:
            mro = cls.__mro__
        except AttributeError:
            try:

                class cls(cls, object):
                    pass

                mro = cls.__mro__[1:]
            except TypeError:
                mro = (object,)

        for t in mro:
            if t in registry:
                return registry[t](*args, **kw)
        else:
            return func(*args, **kw)

    try:
        wrapper.__name__ = func.__name__
    except (TypeError, AttributeError):
        pass

    def register(typ, func=None):
        if func is None:
            return lambda f: register(typ, f)
        else:
            registry[typ] = func
            return func

    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    wrapper.register = register
    return wrapper


def walk_packages(path=None, prefix='', onerror=None):

    def seen(p, m={}):
        if p in m:
            return True
        m[p] = True

    for importer, name, ispkg in iter_modules(path, prefix):
        yield (importer, name, ispkg)
        if ispkg:
            try:
                __import__(name)
            except ImportError:
                if onerror is not None:
                    onerror(name)
            except Exception:
                if onerror is not None:
                    onerror(name)
                else:
                    raise
            else:
                path = getattr(sys.modules[name], '__path__', None) or []
                path = [ p for p in path if not seen(p) ]
                for item in walk_packages(path, name + '.', onerror):
                    yield item

    return


def iter_modules(path=None, prefix=''):
    if path is None:
        importers = iter_importers()
    else:
        importers = map(get_importer, path)
    yielded = {}
    for i in importers:
        for name, ispkg in iter_importer_modules(i, prefix):
            if name not in yielded:
                yielded[name] = 1
                yield (i, name, ispkg)

    return


def iter_importer_modules(importer, prefix=''):
    return [] if not hasattr(importer, 'iter_modules') else importer.iter_modules(prefix)


iter_importer_modules = simplegeneric(iter_importer_modules)

class ImpImporter:

    def __init__(self, path=None):
        self.path = path

    def find_module(self, fullname, path=None):
        subname = fullname.split('.')[-1]
        if subname != fullname and self.path is None:
            return
        else:
            if self.path is None:
                path = None
            else:
                path = [os.path.realpath(self.path)]
            try:
                file, filename, etc = imp.find_module(subname, path)
            except ImportError:
                return

            return ImpLoader(fullname, file, filename, etc)

    def iter_modules(self, prefix=''):
        if self.path is None or not os.path.isdir(self.path):
            return
        else:
            yielded = {}
            import inspect
            try:
                filenames = os.listdir(self.path)
            except OSError:
                filenames = []

            filenames.sort()
            for fn in filenames:
                modname = inspect.getmodulename(fn)
                if modname == '__init__' or modname in yielded:
                    continue
                path = os.path.join(self.path, fn)
                ispkg = False
                if not modname and os.path.isdir(path) and '.' not in fn:
                    modname = fn
                    try:
                        dircontents = os.listdir(path)
                    except OSError:
                        dircontents = []

                    for fn in dircontents:
                        subname = inspect.getmodulename(fn)
                        if subname == '__init__':
                            ispkg = True
                            break
                    else:
                        continue

                if modname and '.' not in modname:
                    yielded[modname] = 1
                    yield (prefix + modname, ispkg)

            return


class ImpLoader:
    code = source = None

    def __init__(self, fullname, file, filename, etc):
        self.file = file
        self.filename = filename
        self.fullname = fullname
        self.etc = etc

    def load_module(self, fullname):
        self._reopen()
        try:
            mod = imp.load_module(fullname, self.file, self.filename, self.etc)
        finally:
            if self.file:
                self.file.close()

        return mod

    def get_data(self, pathname):
        with open(pathname, 'rb') as file:
            return file.read()

    def _reopen(self):
        if self.file and self.file.closed:
            mod_type = self.etc[2]
            if mod_type == imp.PY_SOURCE:
                self.file = open(self.filename, 'rU')
            elif mod_type in (imp.PY_COMPILED, imp.C_EXTENSION):
                self.file = open(self.filename, 'rb')

    def _fix_name(self, fullname):
        if fullname is None:
            fullname = self.fullname
        elif fullname != self.fullname:
            raise ImportError('Loader for module %s cannot handle module %s' % (self.fullname, fullname))
        return fullname

    def is_package(self, fullname):
        fullname = self._fix_name(fullname)
        return self.etc[2] == imp.PKG_DIRECTORY

    def get_code(self, fullname=None):
        fullname = self._fix_name(fullname)
        if self.code is None:
            mod_type = self.etc[2]
            if mod_type == imp.PY_SOURCE:
                source = self.get_source(fullname)
                self.code = compile(source, self.filename, 'exec')
            elif mod_type == imp.PY_COMPILED:
                self._reopen()
                try:
                    self.code = read_code(self.file)
                finally:
                    self.file.close()

            elif mod_type == imp.PKG_DIRECTORY:
                self.code = self._get_delegate().get_code()
        return self.code

    def get_source(self, fullname=None):
        fullname = self._fix_name(fullname)
        if self.source is None:
            mod_type = self.etc[2]
            if mod_type == imp.PY_SOURCE:
                self._reopen()
                try:
                    self.source = self.file.read()
                finally:
                    self.file.close()

            elif mod_type == imp.PY_COMPILED:
                if os.path.exists(self.filename[:-1]):
                    f = open(self.filename[:-1], 'rU')
                    self.source = f.read()
                    f.close()
            elif mod_type == imp.PKG_DIRECTORY:
                self.source = self._get_delegate().get_source()
        return self.source

    def _get_delegate(self):
        return ImpImporter(self.filename).find_module('__init__')

    def get_filename(self, fullname=None):
        fullname = self._fix_name(fullname)
        mod_type = self.etc[2]
        if self.etc[2] == imp.PKG_DIRECTORY:
            return self._get_delegate().get_filename()
        else:
            return self.filename if self.etc[2] in (imp.PY_SOURCE, imp.PY_COMPILED, imp.C_EXTENSION) else None


try:
    import zipimport
    from zipimport import zipimporter

    def iter_zipimport_modules(importer, prefix=''):
        dirlist = zipimport._zip_directory_cache[importer.archive].keys()
        dirlist.sort()
        _prefix = importer.prefix
        plen = len(_prefix)
        yielded = {}
        import inspect
        for fn in dirlist:
            if not fn.startswith(_prefix):
                continue
            fn = fn[plen:].split(os.sep)
            if len(fn) == 2 and fn[1].startswith('__init__.py'):
                if fn[0] not in yielded:
                    yielded[fn[0]] = 1
                    yield (fn[0], True)
            if len(fn) != 1:
                continue
            modname = inspect.getmodulename(fn[0])
            if modname == '__init__':
                continue
            if modname and '.' not in modname and modname not in yielded:
                yielded[modname] = 1
                yield (prefix + modname, False)


    iter_importer_modules.register(zipimporter, iter_zipimport_modules)
except ImportError:
    pass

def get_importer(path_item):
    try:
        importer = sys.path_importer_cache[path_item]
    except KeyError:
        for path_hook in sys.path_hooks:
            try:
                importer = path_hook(path_item)
                break
            except ImportError:
                pass

        else:
            importer = None

        sys.path_importer_cache.setdefault(path_item, importer)

    if importer is None:
        try:
            importer = ImpImporter(path_item)
        except ImportError:
            importer = None

    return importer


def iter_importers(fullname=''):
    if fullname.startswith('.'):
        raise ImportError('Relative module names not supported')
    if '.' in fullname:
        pkg = '.'.join(fullname.split('.')[:-1])
        if pkg not in sys.modules:
            __import__(pkg)
        path = getattr(sys.modules[pkg], '__path__', None) or []
    else:
        for importer in sys.meta_path:
            yield importer

        path = sys.path
    for item in path:
        yield get_importer(item)

    if '.' not in fullname:
        yield ImpImporter()
    return


def get_loader(module_or_name):
    if module_or_name in sys.modules:
        module_or_name = sys.modules[module_or_name]
    if isinstance(module_or_name, ModuleType):
        module = module_or_name
        loader = getattr(module, '__loader__', None)
        if loader is not None:
            return loader
        fullname = module.__name__
    else:
        fullname = module_or_name
    return find_loader(fullname)


def find_loader(fullname):
    for importer in iter_importers(fullname):
        loader = importer.find_module(fullname)
        if loader is not None:
            return loader

    return


def extend_path(path, name):
    if not isinstance(path, list):
        return path
    pname = os.path.join(*name.split('.'))
    sname = os.extsep.join(name.split('.'))
    sname_pkg = sname + os.extsep + 'pkg'
    init_py = '__init__' + os.extsep + 'py'
    path = path[:]
    for dir in sys.path:
        if not isinstance(dir, basestring) or not os.path.isdir(dir):
            continue
        subdir = os.path.join(dir, pname)
        initfile = os.path.join(subdir, init_py)
        if subdir not in path and os.path.isfile(initfile):
            path.append(subdir)
        pkgfile = os.path.join(dir, sname_pkg)
        if os.path.isfile(pkgfile):
            try:
                f = open(pkgfile)
            except IOError as msg:
                sys.stderr.write("Can't open %s: %s\n" % (pkgfile, msg))
            else:
                for line in f:
                    line = line.rstrip('\n')
                    if not line or line.startswith('#'):
                        continue
                    path.append(line)

                f.close()

    return path


def get_data(package, resource):
    loader = get_loader(package)
    if loader is None or not hasattr(loader, 'get_data'):
        return
    else:
        mod = sys.modules.get(package) or loader.load_module(package)
        if mod is None or not hasattr(mod, '__file__'):
            return
        parts = resource.split('/')
        parts.insert(0, os.path.dirname(mod.__file__))
        resource_name = os.path.join(*parts)
        return loader.get_data(resource_name)
