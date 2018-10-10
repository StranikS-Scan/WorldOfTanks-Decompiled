# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/command/build_ext.py
__revision__ = '$Id$'
import sys, os, string, re
from types import *
from site import USER_BASE, USER_SITE
from distutils.core import Command
from distutils.errors import *
from distutils.sysconfig import customize_compiler, get_python_version
from distutils.dep_util import newer_group
from distutils.extension import Extension
from distutils.util import get_platform
from distutils import log
if os.name == 'nt':
    from distutils.msvccompiler import get_build_version
    MSVC_VERSION = int(get_build_version())
extension_name_re = re.compile('^[a-zA-Z_][a-zA-Z_0-9]*(\\.[a-zA-Z_][a-zA-Z_0-9]*)*$')

def show_compilers():
    from distutils.ccompiler import show_compilers
    show_compilers()


class build_ext(Command):
    description = 'build C/C++ extensions (compile/link to build directory)'
    sep_by = " (separated by '%s')" % os.pathsep
    user_options = [('build-lib=', 'b', 'directory for compiled extension modules'),
     ('build-temp=', 't', 'directory for temporary files (build by-products)'),
     ('plat-name=', 'p', 'platform name to cross-compile for, if supported (default: %s)' % get_platform()),
     ('inplace', 'i', 'ignore build-lib and put compiled extensions into the source ' + 'directory alongside your pure Python modules'),
     ('include-dirs=', 'I', 'list of directories to search for header files' + sep_by),
     ('define=', 'D', 'C preprocessor macros to define'),
     ('undef=', 'U', 'C preprocessor macros to undefine'),
     ('libraries=', 'l', 'external C libraries to link with'),
     ('library-dirs=', 'L', 'directories to search for external C libraries' + sep_by),
     ('rpath=', 'R', 'directories to search for shared C libraries at runtime'),
     ('link-objects=', 'O', 'extra explicit link objects to include in the link'),
     ('debug', 'g', 'compile/link with debugging information'),
     ('force', 'f', 'forcibly build everything (ignore file timestamps)'),
     ('compiler=', 'c', 'specify the compiler type'),
     ('swig-cpp', None, 'make SWIG create C++ files (default is C)'),
     ('swig-opts=', None, 'list of SWIG command line options'),
     ('swig=', None, 'path to the SWIG executable'),
     ('user', None, 'add user include, library and rpath')]
    boolean_options = ['inplace',
     'debug',
     'force',
     'swig-cpp',
     'user']
    help_options = [('help-compiler',
      None,
      'list available compilers',
      show_compilers)]

    def initialize_options(self):
        self.extensions = None
        self.build_lib = None
        self.plat_name = None
        self.build_temp = None
        self.inplace = 0
        self.package = None
        self.include_dirs = None
        self.define = None
        self.undef = None
        self.libraries = None
        self.library_dirs = None
        self.rpath = None
        self.link_objects = None
        self.debug = None
        self.force = None
        self.compiler = None
        self.swig = None
        self.swig_cpp = None
        self.swig_opts = None
        self.user = None
        return

    def finalize_options(self):
        from distutils import sysconfig
        self.set_undefined_options('build', ('build_lib', 'build_lib'), ('build_temp', 'build_temp'), ('compiler', 'compiler'), ('debug', 'debug'), ('force', 'force'), ('plat_name', 'plat_name'))
        if self.package is None:
            self.package = self.distribution.ext_package
        self.extensions = self.distribution.ext_modules
        py_include = sysconfig.get_python_inc()
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        if self.include_dirs is None:
            self.include_dirs = self.distribution.include_dirs or []
        if isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)
        self.include_dirs.append(py_include)
        if plat_py_include != py_include:
            self.include_dirs.append(plat_py_include)
        self.ensure_string_list('libraries')
        if self.libraries is None:
            self.libraries = []
        if self.library_dirs is None:
            self.library_dirs = []
        elif type(self.library_dirs) is StringType:
            self.library_dirs = string.split(self.library_dirs, os.pathsep)
        if self.rpath is None:
            self.rpath = []
        elif type(self.rpath) is StringType:
            self.rpath = string.split(self.rpath, os.pathsep)
        if os.name == 'nt':
            self.library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))
            if self.debug:
                self.build_temp = os.path.join(self.build_temp, 'Debug')
            else:
                self.build_temp = os.path.join(self.build_temp, 'Release')
            self.include_dirs.append(os.path.join(sys.exec_prefix, 'PC'))
            if MSVC_VERSION == 9:
                if self.plat_name == 'win32':
                    suffix = ''
                else:
                    suffix = self.plat_name[4:]
                new_lib = os.path.join(sys.exec_prefix, 'PCbuild')
                if suffix:
                    new_lib = os.path.join(new_lib, suffix)
                self.library_dirs.append(new_lib)
            elif MSVC_VERSION == 8:
                self.library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VS8.0'))
            elif MSVC_VERSION == 7:
                self.library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VS7.1'))
            else:
                self.library_dirs.append(os.path.join(sys.exec_prefix, 'PC', 'VC6'))
        if os.name == 'os2':
            self.library_dirs.append(os.path.join(sys.exec_prefix, 'Config'))
        if sys.platform[:6] == 'cygwin' or sys.platform[:6] == 'atheos':
            if sys.executable.startswith(os.path.join(sys.exec_prefix, 'bin')):
                self.library_dirs.append(os.path.join(sys.prefix, 'lib', 'python' + get_python_version(), 'config'))
            else:
                self.library_dirs.append('.')
        if sysconfig.get_config_var('Py_ENABLE_SHARED'):
            if sys.executable.startswith(os.path.join(sys.exec_prefix, 'bin')):
                self.library_dirs.append(sysconfig.get_config_var('LIBDIR'))
            else:
                self.library_dirs.append('.')
        if self.define:
            defines = self.define.split(',')
            self.define = map(lambda symbol: (symbol, '1'), defines)
        if self.undef:
            self.undef = self.undef.split(',')
        if self.swig_opts is None:
            self.swig_opts = []
        else:
            self.swig_opts = self.swig_opts.split(' ')
        if self.user:
            user_include = os.path.join(USER_BASE, 'include')
            user_lib = os.path.join(USER_BASE, 'lib')
            if os.path.isdir(user_include):
                self.include_dirs.append(user_include)
            if os.path.isdir(user_lib):
                self.library_dirs.append(user_lib)
                self.rpath.append(user_lib)
        return

    def run(self):
        from distutils.ccompiler import new_compiler
        if not self.extensions:
            return
        else:
            if self.distribution.has_c_libraries():
                build_clib = self.get_finalized_command('build_clib')
                self.libraries.extend(build_clib.get_library_names() or [])
                self.library_dirs.append(build_clib.build_clib)
            self.compiler = new_compiler(compiler=self.compiler, verbose=self.verbose, dry_run=self.dry_run, force=self.force)
            customize_compiler(self.compiler)
            if os.name == 'nt' and self.plat_name != get_platform():
                self.compiler.initialize(self.plat_name)
            if self.include_dirs is not None:
                self.compiler.set_include_dirs(self.include_dirs)
            if self.define is not None:
                for name, value in self.define:
                    self.compiler.define_macro(name, value)

            if self.undef is not None:
                for macro in self.undef:
                    self.compiler.undefine_macro(macro)

            if self.libraries is not None:
                self.compiler.set_libraries(self.libraries)
            if self.library_dirs is not None:
                self.compiler.set_library_dirs(self.library_dirs)
            if self.rpath is not None:
                self.compiler.set_runtime_library_dirs(self.rpath)
            if self.link_objects is not None:
                self.compiler.set_link_objects(self.link_objects)
            self.build_extensions()
            return

    def check_extensions_list(self, extensions):
        if not isinstance(extensions, list):
            raise DistutilsSetupError, "'ext_modules' option must be a list of Extension instances"
        for i, ext in enumerate(extensions):
            if isinstance(ext, Extension):
                continue
            if not isinstance(ext, tuple) or len(ext) != 2:
                raise DistutilsSetupError, "each element of 'ext_modules' option must be an Extension instance or 2-tuple"
            ext_name, build_info = ext
            log.warn("old-style (ext_name, build_info) tuple found in ext_modules for extension '%s'-- please convert to Extension instance" % ext_name)
            if not (isinstance(ext_name, str) and extension_name_re.match(ext_name)):
                raise DistutilsSetupError, "first element of each tuple in 'ext_modules' must be the extension name (a string)"
            if not isinstance(build_info, dict):
                raise DistutilsSetupError, "second element of each tuple in 'ext_modules' must be a dictionary (build info)"
            ext = Extension(ext_name, build_info['sources'])
            for key in ('include_dirs', 'library_dirs', 'libraries', 'extra_objects', 'extra_compile_args', 'extra_link_args'):
                val = build_info.get(key)
                if val is not None:
                    setattr(ext, key, val)

            ext.runtime_library_dirs = build_info.get('rpath')
            if 'def_file' in build_info:
                log.warn("'def_file' element of build info dict no longer supported")
            macros = build_info.get('macros')
            if macros:
                ext.define_macros = []
                ext.undef_macros = []
                for macro in macros:
                    if not (isinstance(macro, tuple) and len(macro) in (1, 2)):
                        raise DistutilsSetupError, "'macros' element of build info dict must be 1- or 2-tuple"
                    if len(macro) == 1:
                        ext.undef_macros.append(macro[0])
                    if len(macro) == 2:
                        ext.define_macros.append(macro)

            extensions[i] = ext

        return

    def get_source_files(self):
        self.check_extensions_list(self.extensions)
        filenames = []
        for ext in self.extensions:
            filenames.extend(ext.sources)

        return filenames

    def get_outputs(self):
        self.check_extensions_list(self.extensions)
        outputs = []
        for ext in self.extensions:
            outputs.append(self.get_ext_fullpath(ext.name))

        return outputs

    def build_extensions(self):
        self.check_extensions_list(self.extensions)
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        sources = ext.sources
        if sources is None or type(sources) not in (ListType, TupleType):
            raise DistutilsSetupError, ("in 'ext_modules' option (extension '%s'), " + "'sources' must be present and must be " + 'a list of source filenames') % ext.name
        sources = list(sources)
        ext_path = self.get_ext_fullpath(ext.name)
        depends = sources + ext.depends
        if not (self.force or newer_group(depends, ext_path, 'newer')):
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            return
        else:
            log.info("building '%s' extension", ext.name)
            sources = self.swig_sources(sources, ext)
            extra_args = ext.extra_compile_args or []
            macros = ext.define_macros[:]
            for undef in ext.undef_macros:
                macros.append((undef,))

            objects = self.compiler.compile(sources, output_dir=self.build_temp, macros=macros, include_dirs=ext.include_dirs, debug=self.debug, extra_postargs=extra_args, depends=ext.depends)
            self._built_objects = objects[:]
            if ext.extra_objects:
                objects.extend(ext.extra_objects)
            extra_args = ext.extra_link_args or []
            language = ext.language or self.compiler.detect_language(sources)
            self.compiler.link_shared_object(objects, ext_path, libraries=self.get_libraries(ext), library_dirs=ext.library_dirs, runtime_library_dirs=ext.runtime_library_dirs, extra_postargs=extra_args, export_symbols=self.get_export_symbols(ext), debug=self.debug, build_temp=self.build_temp, target_lang=language)
            return

    def swig_sources(self, sources, extension):
        new_sources = []
        swig_sources = []
        swig_targets = {}
        if self.swig_cpp:
            log.warn('--swig-cpp is deprecated - use --swig-opts=-c++')
        if self.swig_cpp or '-c++' in self.swig_opts or '-c++' in extension.swig_opts:
            target_ext = '.cpp'
        else:
            target_ext = '.c'
        for source in sources:
            base, ext = os.path.splitext(source)
            if ext == '.i':
                new_sources.append(base + '_wrap' + target_ext)
                swig_sources.append(source)
                swig_targets[source] = new_sources[-1]
            new_sources.append(source)

        if not swig_sources:
            return new_sources
        swig = self.swig or self.find_swig()
        swig_cmd = [swig, '-python']
        swig_cmd.extend(self.swig_opts)
        if self.swig_cpp:
            swig_cmd.append('-c++')
        if not self.swig_opts:
            for o in extension.swig_opts:
                swig_cmd.append(o)

        for source in swig_sources:
            target = swig_targets[source]
            log.info('swigging %s to %s', source, target)
            self.spawn(swig_cmd + ['-o', target, source])

        return new_sources

    def find_swig(self):
        if os.name == 'posix':
            return 'swig'
        if os.name == 'nt':
            for vers in ('1.3', '1.2', '1.1'):
                fn = os.path.join('c:\\swig%s' % vers, 'swig.exe')
                if os.path.isfile(fn):
                    return fn
            else:
                return 'swig.exe'

        else:
            if os.name == 'os2':
                return 'swig.exe'
            raise DistutilsPlatformError, "I don't know how to find (much less run) SWIG on platform '%s'" % os.name

    def get_ext_fullpath(self, ext_name):
        all_dots = string.maketrans('/' + os.sep, '..')
        ext_name = ext_name.translate(all_dots)
        fullname = self.get_ext_fullname(ext_name)
        modpath = fullname.split('.')
        filename = self.get_ext_filename(ext_name)
        filename = os.path.split(filename)[-1]
        if not self.inplace:
            filename = os.path.join(*(modpath[:-1] + [filename]))
            return os.path.join(self.build_lib, filename)
        package = '.'.join(modpath[0:-1])
        build_py = self.get_finalized_command('build_py')
        package_dir = os.path.abspath(build_py.get_package_dir(package))
        return os.path.join(package_dir, filename)

    def get_ext_fullname(self, ext_name):
        if self.package is None:
            return ext_name
        else:
            return self.package + '.' + ext_name
            return

    def get_ext_filename(self, ext_name):
        from distutils.sysconfig import get_config_var
        ext_path = string.split(ext_name, '.')
        if os.name == 'os2':
            ext_path[len(ext_path) - 1] = ext_path[len(ext_path) - 1][:8]
        so_ext = get_config_var('SO')
        return os.path.join(*ext_path) + '_d' + so_ext if os.name == 'nt' and self.debug else os.path.join(*ext_path) + so_ext

    def get_export_symbols(self, ext):
        initfunc_name = 'init' + ext.name.split('.')[-1]
        if initfunc_name not in ext.export_symbols:
            ext.export_symbols.append(initfunc_name)
        return ext.export_symbols

    def get_libraries(self, ext):
        if sys.platform == 'win32':
            from distutils.msvccompiler import MSVCCompiler
            if not isinstance(self.compiler, MSVCCompiler):
                template = 'python%d%d'
                if self.debug:
                    template = template + '_d'
                pythonlib = template % (sys.hexversion >> 24, sys.hexversion >> 16 & 255)
                return ext.libraries + [pythonlib]
            else:
                return ext.libraries
        else:
            if sys.platform == 'os2emx':
                template = 'python%d%d'
                pythonlib = template % (sys.hexversion >> 24, sys.hexversion >> 16 & 255)
                return ext.libraries + [pythonlib]
            if sys.platform[:6] == 'cygwin':
                template = 'python%d.%d'
                pythonlib = template % (sys.hexversion >> 24, sys.hexversion >> 16 & 255)
                return ext.libraries + [pythonlib]
            if sys.platform[:6] == 'atheos':
                from distutils import sysconfig
                template = 'python%d.%d'
                pythonlib = template % (sys.hexversion >> 24, sys.hexversion >> 16 & 255)
                extra = []
                for lib in sysconfig.get_config_var('SHLIBS').split():
                    if lib.startswith('-l'):
                        extra.append(lib[2:])
                    extra.append(lib)

                return ext.libraries + [pythonlib, 'm'] + extra
            if sys.platform == 'darwin':
                return ext.libraries
            if sys.platform[:3] == 'aix':
                return ext.libraries
            from distutils import sysconfig
            if sysconfig.get_config_var('Py_ENABLE_SHARED'):
                template = 'python%d.%d'
                pythonlib = template % (sys.hexversion >> 24, sys.hexversion >> 16 & 255)
                return ext.libraries + [pythonlib]
            return ext.libraries
