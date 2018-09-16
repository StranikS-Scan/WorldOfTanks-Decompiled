# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/ccompiler.py
__revision__ = '$Id$'
import sys
import os
import re
from distutils.errors import CompileError, LinkError, UnknownFileError, DistutilsPlatformError, DistutilsModuleError
from distutils.spawn import spawn
from distutils.file_util import move_file
from distutils.dir_util import mkpath
from distutils.dep_util import newer_group
from distutils.util import split_quoted, execute
from distutils import log
from distutils.sysconfig import customize_compiler

class CCompiler():
    compiler_type = None
    src_extensions = None
    obj_extension = None
    static_lib_extension = None
    shared_lib_extension = None
    static_lib_format = None
    shared_lib_format = None
    exe_extension = None
    language_map = {'.c': 'c',
     '.cc': 'c++',
     '.cpp': 'c++',
     '.cxx': 'c++',
     '.m': 'objc'}
    language_order = ['c++', 'objc', 'c']

    def __init__(self, verbose=0, dry_run=0, force=0):
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose
        self.output_dir = None
        self.macros = []
        self.include_dirs = []
        self.libraries = []
        self.library_dirs = []
        self.runtime_library_dirs = []
        self.objects = []
        for key in self.executables.keys():
            self.set_executable(key, self.executables[key])

        return

    def set_executables(self, **args):
        for key in args.keys():
            if key not in self.executables:
                raise ValueError, "unknown executable '%s' for class %s" % (key, self.__class__.__name__)
            self.set_executable(key, args[key])

    def set_executable(self, key, value):
        if isinstance(value, str):
            setattr(self, key, split_quoted(value))
        else:
            setattr(self, key, value)

    def _find_macro(self, name):
        i = 0
        for defn in self.macros:
            if defn[0] == name:
                return i
            i = i + 1

        return None

    def _check_macro_definitions(self, definitions):
        for defn in definitions:
            if not (isinstance(defn, tuple) and (len(defn) == 1 or len(defn) == 2 and (isinstance(defn[1], str) or defn[1] is None)) and isinstance(defn[0], str)):
                raise TypeError, "invalid macro definition '%s': " % defn + 'must be tuple (string,), (string, string), or ' + '(string, None)'

        return

    def define_macro(self, name, value=None):
        i = self._find_macro(name)
        if i is not None:
            del self.macros[i]
        defn = (name, value)
        self.macros.append(defn)
        return

    def undefine_macro(self, name):
        i = self._find_macro(name)
        if i is not None:
            del self.macros[i]
        undefn = (name,)
        self.macros.append(undefn)
        return

    def add_include_dir(self, dir):
        self.include_dirs.append(dir)

    def set_include_dirs(self, dirs):
        self.include_dirs = dirs[:]

    def add_library(self, libname):
        self.libraries.append(libname)

    def set_libraries(self, libnames):
        self.libraries = libnames[:]

    def add_library_dir(self, dir):
        self.library_dirs.append(dir)

    def set_library_dirs(self, dirs):
        self.library_dirs = dirs[:]

    def add_runtime_library_dir(self, dir):
        self.runtime_library_dirs.append(dir)

    def set_runtime_library_dirs(self, dirs):
        self.runtime_library_dirs = dirs[:]

    def add_link_object(self, object):
        self.objects.append(object)

    def set_link_objects(self, objects):
        self.objects = objects[:]

    def _setup_compile(self, outdir, macros, incdirs, sources, depends, extra):
        if outdir is None:
            outdir = self.output_dir
        elif not isinstance(outdir, str):
            raise TypeError, "'output_dir' must be a string or None"
        if macros is None:
            macros = self.macros
        elif isinstance(macros, list):
            macros = macros + (self.macros or [])
        else:
            raise TypeError, "'macros' (if supplied) must be a list of tuples"
        if incdirs is None:
            incdirs = self.include_dirs
        elif isinstance(incdirs, (list, tuple)):
            incdirs = list(incdirs) + (self.include_dirs or [])
        else:
            raise TypeError, "'include_dirs' (if supplied) must be a list of strings"
        if extra is None:
            extra = []
        objects = self.object_filenames(sources, strip_dir=0, output_dir=outdir)
        pp_opts = gen_preprocess_options(macros, incdirs)
        build = {}
        for i in range(len(sources)):
            src = sources[i]
            obj = objects[i]
            ext = os.path.splitext(src)[1]
            self.mkpath(os.path.dirname(obj))
            build[obj] = (src, ext)

        return (macros,
         objects,
         extra,
         pp_opts,
         build)

    def _get_cc_args(self, pp_opts, debug, before):
        cc_args = pp_opts + ['-c']
        if debug:
            cc_args[:0] = ['-g']
        if before:
            cc_args[:0] = before
        return cc_args

    def _fix_compile_args(self, output_dir, macros, include_dirs):
        if output_dir is None:
            output_dir = self.output_dir
        elif not isinstance(output_dir, str):
            raise TypeError, "'output_dir' must be a string or None"
        if macros is None:
            macros = self.macros
        elif isinstance(macros, list):
            macros = macros + (self.macros or [])
        else:
            raise TypeError, "'macros' (if supplied) must be a list of tuples"
        if include_dirs is None:
            include_dirs = self.include_dirs
        elif isinstance(include_dirs, (list, tuple)):
            include_dirs = list(include_dirs) + (self.include_dirs or [])
        else:
            raise TypeError, "'include_dirs' (if supplied) must be a list of strings"
        return (output_dir, macros, include_dirs)

    def _fix_object_args(self, objects, output_dir):
        if not isinstance(objects, (list, tuple)):
            raise TypeError, "'objects' must be a list or tuple of strings"
        objects = list(objects)
        if output_dir is None:
            output_dir = self.output_dir
        elif not isinstance(output_dir, str):
            raise TypeError, "'output_dir' must be a string or None"
        return (objects, output_dir)

    def _fix_lib_args(self, libraries, library_dirs, runtime_library_dirs):
        if libraries is None:
            libraries = self.libraries
        elif isinstance(libraries, (list, tuple)):
            libraries = list(libraries) + (self.libraries or [])
        else:
            raise TypeError, "'libraries' (if supplied) must be a list of strings"
        if library_dirs is None:
            library_dirs = self.library_dirs
        elif isinstance(library_dirs, (list, tuple)):
            library_dirs = list(library_dirs) + (self.library_dirs or [])
        else:
            raise TypeError, "'library_dirs' (if supplied) must be a list of strings"
        if runtime_library_dirs is None:
            runtime_library_dirs = self.runtime_library_dirs
        elif isinstance(runtime_library_dirs, (list, tuple)):
            runtime_library_dirs = list(runtime_library_dirs) + (self.runtime_library_dirs or [])
        else:
            raise TypeError, "'runtime_library_dirs' (if supplied) " + 'must be a list of strings'
        return (libraries, library_dirs, runtime_library_dirs)

    def _need_link(self, objects, output_file):
        if self.force:
            return 1
        else:
            if self.dry_run:
                newer = newer_group(objects, output_file, missing='newer')
            else:
                newer = newer_group(objects, output_file)
            return newer

    def detect_language(self, sources):
        if not isinstance(sources, list):
            sources = [sources]
        lang = None
        index = len(self.language_order)
        for source in sources:
            base, ext = os.path.splitext(source)
            extlang = self.language_map.get(ext)
            try:
                extindex = self.language_order.index(extlang)
                if extindex < index:
                    lang = extlang
                    index = extindex
            except ValueError:
                pass

        return lang

    def preprocess(self, source, output_file=None, macros=None, include_dirs=None, extra_preargs=None, extra_postargs=None):
        pass

    def compile(self, sources, output_dir=None, macros=None, include_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, depends=None):
        macros, objects, extra_postargs, pp_opts, build = self._setup_compile(output_dir, macros, include_dirs, sources, depends, extra_postargs)
        cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
        for obj in objects:
            try:
                src, ext = build[obj]
            except KeyError:
                continue

            self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)

        return objects

    def _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        pass

    def create_static_lib(self, objects, output_libname, output_dir=None, debug=0, target_lang=None):
        pass

    SHARED_OBJECT = 'shared_object'
    SHARED_LIBRARY = 'shared_library'
    EXECUTABLE = 'executable'

    def link(self, target_desc, objects, output_filename, output_dir=None, libraries=None, library_dirs=None, runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None, build_temp=None, target_lang=None):
        raise NotImplementedError

    def link_shared_lib(self, objects, output_libname, output_dir=None, libraries=None, library_dirs=None, runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None, build_temp=None, target_lang=None):
        self.link(CCompiler.SHARED_LIBRARY, objects, self.library_filename(output_libname, lib_type='shared'), output_dir, libraries, library_dirs, runtime_library_dirs, export_symbols, debug, extra_preargs, extra_postargs, build_temp, target_lang)

    def link_shared_object(self, objects, output_filename, output_dir=None, libraries=None, library_dirs=None, runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None, build_temp=None, target_lang=None):
        self.link(CCompiler.SHARED_OBJECT, objects, output_filename, output_dir, libraries, library_dirs, runtime_library_dirs, export_symbols, debug, extra_preargs, extra_postargs, build_temp, target_lang)

    def link_executable(self, objects, output_progname, output_dir=None, libraries=None, library_dirs=None, runtime_library_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, target_lang=None):
        self.link(CCompiler.EXECUTABLE, objects, self.executable_filename(output_progname), output_dir, libraries, library_dirs, runtime_library_dirs, None, debug, extra_preargs, extra_postargs, None, target_lang)
        return

    def library_dir_option(self, dir):
        raise NotImplementedError

    def runtime_library_dir_option(self, dir):
        raise NotImplementedError

    def library_option(self, lib):
        raise NotImplementedError

    def has_function(self, funcname, includes=None, include_dirs=None, libraries=None, library_dirs=None):
        import tempfile
        if includes is None:
            includes = []
        if include_dirs is None:
            include_dirs = []
        if libraries is None:
            libraries = []
        if library_dirs is None:
            library_dirs = []
        fd, fname = tempfile.mkstemp('.c', funcname, text=True)
        f = os.fdopen(fd, 'w')
        try:
            for incl in includes:
                f.write('#include "%s"\n' % incl)

            f.write('main (int argc, char **argv) {\n    %s();\n}\n' % funcname)
        finally:
            f.close()

        try:
            objects = self.compile([fname], include_dirs=include_dirs)
        except CompileError:
            return False

        try:
            self.link_executable(objects, 'a.out', libraries=libraries, library_dirs=library_dirs)
        except (LinkError, TypeError):
            return False

        return True

    def find_library_file(self, dirs, lib, debug=0):
        raise NotImplementedError

    def object_filenames(self, source_filenames, strip_dir=0, output_dir=''):
        if output_dir is None:
            output_dir = ''
        obj_names = []
        for src_name in source_filenames:
            base, ext = os.path.splitext(src_name)
            base = os.path.splitdrive(base)[1]
            base = base[os.path.isabs(base):]
            if ext not in self.src_extensions:
                raise UnknownFileError, "unknown file type '%s' (from '%s')" % (ext, src_name)
            if strip_dir:
                base = os.path.basename(base)
            obj_names.append(os.path.join(output_dir, base + self.obj_extension))

        return obj_names

    def shared_object_filename(self, basename, strip_dir=0, output_dir=''):
        if strip_dir:
            basename = os.path.basename(basename)
        return os.path.join(output_dir, basename + self.shared_lib_extension)

    def executable_filename(self, basename, strip_dir=0, output_dir=''):
        if strip_dir:
            basename = os.path.basename(basename)
        return os.path.join(output_dir, basename + (self.exe_extension or ''))

    def library_filename(self, libname, lib_type='static', strip_dir=0, output_dir=''):
        if lib_type not in ('static', 'shared', 'dylib'):
            raise ValueError, '\'lib_type\' must be "static", "shared" or "dylib"'
        fmt = getattr(self, lib_type + '_lib_format')
        ext = getattr(self, lib_type + '_lib_extension')
        dir, base = os.path.split(libname)
        filename = fmt % (base, ext)
        if strip_dir:
            dir = ''
        return os.path.join(output_dir, dir, filename)

    def announce(self, msg, level=1):
        log.debug(msg)

    def debug_print(self, msg):
        from distutils.debug import DEBUG
        if DEBUG:
            print msg

    def warn(self, msg):
        sys.stderr.write('warning: %s\n' % msg)

    def execute(self, func, args, msg=None, level=1):
        execute(func, args, msg, self.dry_run)

    def spawn(self, cmd):
        spawn(cmd, dry_run=self.dry_run)

    def move_file(self, src, dst):
        return move_file(src, dst, dry_run=self.dry_run)

    def mkpath(self, name, mode=511):
        mkpath(name, mode, dry_run=self.dry_run)


_default_compilers = (('cygwin.*', 'unix'),
 ('os2emx', 'emx'),
 ('posix', 'unix'),
 ('nt', 'msvc'))

def get_default_compiler(osname=None, platform=None):
    if osname is None:
        osname = os.name
    if platform is None:
        platform = sys.platform
    for pattern, compiler in _default_compilers:
        if re.match(pattern, platform) is not None or re.match(pattern, osname) is not None:
            return compiler

    return 'unix'


compiler_class = {'unix': ('unixccompiler', 'UnixCCompiler', 'standard UNIX-style compiler'),
 'msvc': ('msvccompiler', 'MSVCCompiler', 'Microsoft Visual C++'),
 'cygwin': ('cygwinccompiler', 'CygwinCCompiler', 'Cygwin port of GNU C Compiler for Win32'),
 'mingw32': ('cygwinccompiler', 'Mingw32CCompiler', 'Mingw32 port of GNU C Compiler for Win32'),
 'bcpp': ('bcppcompiler', 'BCPPCompiler', 'Borland C++ Compiler'),
 'emx': ('emxccompiler', 'EMXCCompiler', 'EMX port of GNU C Compiler for OS/2')}

def show_compilers():
    from distutils.fancy_getopt import FancyGetopt
    compilers = []
    for compiler in compiler_class.keys():
        compilers.append(('compiler=' + compiler, None, compiler_class[compiler][2]))

    compilers.sort()
    pretty_printer = FancyGetopt(compilers)
    pretty_printer.print_help('List of available compilers:')
    return


def new_compiler(plat=None, compiler=None, verbose=0, dry_run=0, force=0):
    if plat is None:
        plat = os.name
    try:
        if compiler is None:
            compiler = get_default_compiler(plat)
        module_name, class_name, long_description = compiler_class[compiler]
    except KeyError:
        msg = "don't know how to compile C/C++ code on platform '%s'" % plat
        if compiler is not None:
            msg = msg + " with '%s' compiler" % compiler
        raise DistutilsPlatformError, msg

    try:
        module_name = 'distutils.' + module_name
        __import__(module_name)
        module = sys.modules[module_name]
        klass = vars(module)[class_name]
    except ImportError:
        raise DistutilsModuleError, "can't compile C/C++ code: unable to load module '%s'" % module_name
    except KeyError:
        raise DistutilsModuleError, ("can't compile C/C++ code: unable to find class '%s' " + "in module '%s'") % (class_name, module_name)

    return klass(None, dry_run, force)


def gen_preprocess_options(macros, include_dirs):
    pp_opts = []
    for macro in macros:
        if not (isinstance(macro, tuple) and 1 <= len(macro) <= 2):
            raise TypeError, ("bad macro definition '%s': " + "each element of 'macros' list must be a 1- or 2-tuple") % macro
        if len(macro) == 1:
            pp_opts.append('-U%s' % macro[0])
        if len(macro) == 2:
            if macro[1] is None:
                pp_opts.append('-D%s' % macro[0])
            else:
                pp_opts.append('-D%s=%s' % macro)

    for dir in include_dirs:
        pp_opts.append('-I%s' % dir)

    return pp_opts


def gen_lib_options(compiler, library_dirs, runtime_library_dirs, libraries):
    lib_opts = []
    for dir in library_dirs:
        lib_opts.append(compiler.library_dir_option(dir))

    for dir in runtime_library_dirs:
        opt = compiler.runtime_library_dir_option(dir)
        if isinstance(opt, list):
            lib_opts.extend(opt)
        lib_opts.append(opt)

    for lib in libraries:
        lib_dir, lib_name = os.path.split(lib)
        if lib_dir != '':
            lib_file = compiler.find_library_file([lib_dir], lib_name)
            if lib_file is not None:
                lib_opts.append(lib_file)
            else:
                compiler.warn("no library file corresponding to '%s' found (skipping)" % lib)
        lib_opts.append(compiler.library_option(lib))

    return lib_opts
