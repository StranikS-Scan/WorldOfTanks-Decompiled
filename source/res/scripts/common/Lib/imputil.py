# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/imputil.py
from warnings import warnpy3k
warnpy3k('the imputil module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
import imp
import sys
import __builtin__
import struct
import marshal
__all__ = ['ImportManager', 'Importer', 'BuiltinImporter']
_StringType = type('')
_ModuleType = type(sys)

class ImportManager:

    def install(self, namespace=vars(__builtin__)):
        if isinstance(namespace, _ModuleType):
            namespace = vars(namespace)
        self.previous_importer = namespace['__import__']
        self.namespace = namespace
        namespace['__import__'] = self._import_hook

    def uninstall(self):
        self.namespace['__import__'] = self.previous_importer

    def add_suffix(self, suffix, importFunc):
        self.fs_imp.add_suffix(suffix, importFunc)

    clsFilesystemImporter = None

    def __init__(self, fs_imp=None):
        global _os_stat
        if not _os_stat:
            _os_bootstrap()
        if fs_imp is None:
            cls = self.clsFilesystemImporter or _FilesystemImporter
            fs_imp = cls()
        self.fs_imp = fs_imp
        for desc in imp.get_suffixes():
            if desc[2] == imp.C_EXTENSION:
                self.add_suffix(desc[0], DynLoadSuffixImporter(desc).import_file)

        self.add_suffix('.py', py_suffix_importer)
        return

    def _import_hook(self, fqname, globals=None, locals=None, fromlist=None):
        parts = fqname.split('.')
        parent = self._determine_import_context(globals)
        if parent:
            module = parent.__importer__._do_import(parent, parts, fromlist)
            if module:
                return module
        try:
            top_module = sys.modules[parts[0]]
        except KeyError:
            top_module = self._import_top_module(parts[0])
            if not top_module:
                raise ImportError, 'No module named ' + fqname

        if len(parts) == 1:
            if not fromlist:
                return top_module
            if not top_module.__dict__.get('__ispkg__'):
                return top_module
        importer = top_module.__dict__.get('__importer__')
        if importer:
            return importer._finish_import(top_module, parts[1:], fromlist)
        if len(parts) == 2 and hasattr(top_module, parts[1]):
            if fromlist:
                return getattr(top_module, parts[1])
            else:
                return top_module
        raise ImportError, 'No module named ' + fqname

    def _determine_import_context(self, globals):
        if not globals or not globals.get('__importer__'):
            return None
        else:
            parent_fqname = globals['__name__']
            if globals['__ispkg__']:
                parent = sys.modules[parent_fqname]
                return parent
            i = parent_fqname.rfind('.')
            if i == -1:
                return None
            parent_fqname = parent_fqname[:i]
            parent = sys.modules[parent_fqname]
            return parent

    def _import_top_module(self, name):
        for item in sys.path:
            if isinstance(item, _StringType):
                module = self.fs_imp.import_from_dir(item, name)
            else:
                module = item.import_top(name)
            if module:
                return module

        return None

    def _reload_hook(self, module):
        importer = module.__dict__.get('__importer__')
        if not importer:
            pass
        raise SystemError, 'reload not yet implemented'


class Importer:

    def import_top(self, name):
        return self._import_one(None, name, name)

    def _finish_import(self, top, parts, fromlist):
        bottom = self._load_tail(top, parts)
        if not fromlist:
            return top
        if bottom.__ispkg__:
            self._import_fromlist(bottom, fromlist)
        return bottom

    def _import_one(self, parent, modname, fqname):
        try:
            return sys.modules[fqname]
        except KeyError:
            pass

        result = self.get_code(parent, modname, fqname)
        if result is None:
            return
        else:
            module = self._process_result(result, fqname)
            if parent:
                setattr(parent, modname, module)
            return module

    def _process_result(self, result, fqname):
        ispkg, code, values = result
        is_module = isinstance(code, _ModuleType)
        if is_module:
            module = code
        else:
            module = imp.new_module(fqname)
        module.__importer__ = self
        module.__ispkg__ = ispkg
        module.__dict__.update(values)
        sys.modules[fqname] = module
        if not is_module:
            try:
                exec code in module.__dict__
            except:
                if fqname in sys.modules:
                    del sys.modules[fqname]
                raise

        module = sys.modules[fqname]
        module.__name__ = fqname
        return module

    def _load_tail(self, m, parts):
        for part in parts:
            fqname = '%s.%s' % (m.__name__, part)
            m = self._import_one(m, part, fqname)
            if not m:
                raise ImportError, 'No module named ' + fqname

        return m

    def _import_fromlist(self, package, fromlist):
        if '*' in fromlist:
            fromlist = list(fromlist) + list(package.__dict__.get('__all__', []))
        for sub in fromlist:
            if sub != '*' and not hasattr(package, sub):
                subname = '%s.%s' % (package.__name__, sub)
                submod = self._import_one(package, sub, subname)
                if not submod:
                    raise ImportError, 'cannot import name ' + subname

    def _do_import(self, parent, parts, fromlist):
        top_name = parts[0]
        top_fqname = parent.__name__ + '.' + top_name
        top_module = self._import_one(parent, top_name, top_fqname)
        return None if not top_module else self._finish_import(top_module, parts[1:], fromlist)

    def get_code(self, parent, modname, fqname):
        raise RuntimeError, 'get_code not implemented'


_suffix_char = __debug__ and 'c' or 'o'
_suffix = '.py' + _suffix_char

def _compile(pathname, timestamp):
    codestring = open(pathname, 'rU').read()
    if codestring and codestring[-1] != '\n':
        codestring = codestring + '\n'
    code = __builtin__.compile(codestring, pathname, 'exec')
    try:
        f = open(pathname + _suffix_char, 'wb')
    except IOError:
        pass
    else:
        f.write('\x00\x00\x00\x00')
        f.write(struct.pack('<I', timestamp))
        marshal.dump(code, f)
        f.flush()
        f.seek(0, 0)
        f.write(imp.get_magic())
        f.close()

    return code


_os_stat = _os_path_join = None

def _os_bootstrap():
    global _os_path_join
    global _os_stat
    names = sys.builtin_module_names
    join = None
    if 'posix' in names:
        sep = '/'
        from posix import stat
    elif 'nt' in names:
        sep = '\\'
        from nt import stat
    elif 'dos' in names:
        sep = '\\'
        from dos import stat
    elif 'os2' in names:
        sep = '\\'
        from os2 import stat
    else:
        raise ImportError, 'no os specific module found'
    if join is None:

        def join(a, b, sep=sep):
            if a == '':
                return b
            lastchar = a[-1:]
            return a + b if lastchar == '/' or lastchar == sep else a + sep + b

    _os_stat = stat
    _os_path_join = join
    return


def _os_path_isdir(pathname):
    try:
        s = _os_stat(pathname)
    except OSError:
        return None

    return s.st_mode & 61440 == 16384


def _timestamp(pathname):
    try:
        s = _os_stat(pathname)
    except OSError:
        return None

    return long(s.st_mtime)


class BuiltinImporter(Importer):

    def get_code(self, parent, modname, fqname):
        if parent:
            return
        else:
            if imp.is_builtin(modname):
                type = imp.C_BUILTIN
            elif imp.is_frozen(modname):
                type = imp.PY_FROZEN
            else:
                return
            module = imp.load_module(modname, None, modname, ('', '', type))
            return (0, module, {})


class _FilesystemImporter(Importer):

    def __init__(self):
        self.suffixes = []

    def add_suffix(self, suffix, importFunc):
        self.suffixes.append((suffix, importFunc))

    def import_from_dir(self, dir, fqname):
        result = self._import_pathname(_os_path_join(dir, fqname), fqname)
        return self._process_result(result, fqname) if result else None

    def get_code(self, parent, modname, fqname):
        for submodule_path in parent.__path__:
            code = self._import_pathname(_os_path_join(submodule_path, modname), fqname)
            if code is not None:
                return code

        return self._import_pathname(_os_path_join(parent.__pkgdir__, modname), fqname)

    def _import_pathname(self, pathname, fqname):
        if _os_path_isdir(pathname):
            result = self._import_pathname(_os_path_join(pathname, '__init__'), fqname)
            if result:
                values = result[2]
                values['__pkgdir__'] = pathname
                values['__path__'] = [pathname]
                return (1, result[1], values)
            return None
        else:
            for suffix, importFunc in self.suffixes:
                filename = pathname + suffix
                try:
                    finfo = _os_stat(filename)
                except OSError:
                    pass
                else:
                    return importFunc(filename, finfo, fqname)

            return None


def py_suffix_importer(filename, finfo, fqname):
    file = filename[:-3] + _suffix
    t_py = long(finfo[8])
    t_pyc = _timestamp(file)
    code = None
    if t_pyc is not None and t_pyc >= t_py:
        f = open(file, 'rb')
        if f.read(4) == imp.get_magic():
            t = struct.unpack('<I', f.read(4))[0]
            if t == t_py:
                code = marshal.load(f)
        f.close()
    if code is None:
        file = filename
        code = _compile(file, t_py)
    return (0, code, {'__file__': file})


class DynLoadSuffixImporter:

    def __init__(self, desc):
        self.desc = desc

    def import_file(self, filename, finfo, fqname):
        fp = open(filename, self.desc[1])
        module = imp.load_module(fqname, fp, filename, self.desc)
        module.__file__ = filename
        return (0, module, {})


def _print_importers():
    items = sys.modules.items()
    items.sort()
    for name, module in items:
        if module:
            print name, module.__dict__.get('__importer__', '-- no importer')
        print name, '-- non-existent module'


def _test_revamp():
    ImportManager().install()
    sys.path.insert(0, BuiltinImporter())
