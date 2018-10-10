# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/unixccompiler.py
__revision__ = '$Id$'
import os, sys, re
from types import StringType, NoneType
from distutils import sysconfig
from distutils.dep_util import newer
from distutils.ccompiler import CCompiler, gen_preprocess_options, gen_lib_options
from distutils.errors import DistutilsExecError, CompileError, LibError, LinkError
from distutils import log
if sys.platform == 'darwin':
    import _osx_support

class UnixCCompiler(CCompiler):
    compiler_type = 'unix'
    executables = {'preprocessor': None,
     'compiler': ['cc'],
     'compiler_so': ['cc'],
     'compiler_cxx': ['cc'],
     'linker_so': ['cc', '-shared'],
     'linker_exe': ['cc'],
     'archiver': ['ar', '-cr'],
     'ranlib': None}
    if sys.platform[:6] == 'darwin':
        executables['ranlib'] = ['ranlib']
    src_extensions = ['.c',
     '.C',
     '.cc',
     '.cxx',
     '.cpp',
     '.m']
    obj_extension = '.o'
    static_lib_extension = '.a'
    shared_lib_extension = '.so'
    dylib_lib_extension = '.dylib'
    static_lib_format = shared_lib_format = dylib_lib_format = 'lib%s%s'
    if sys.platform == 'cygwin':
        exe_extension = '.exe'

    def preprocess(self, source, output_file=None, macros=None, include_dirs=None, extra_preargs=None, extra_postargs=None):
        ignore, macros, include_dirs = self._fix_compile_args(None, macros, include_dirs)
        pp_opts = gen_preprocess_options(macros, include_dirs)
        pp_args = self.preprocessor + pp_opts
        if output_file:
            pp_args.extend(['-o', output_file])
        if extra_preargs:
            pp_args[:0] = extra_preargs
        if extra_postargs:
            pp_args.extend(extra_postargs)
        pp_args.append(source)
        if self.force or output_file is None or newer(source, output_file):
            if output_file:
                self.mkpath(os.path.dirname(output_file))
            try:
                self.spawn(pp_args)
            except DistutilsExecError as msg:
                raise CompileError, msg

        return

    def _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        compiler_so = self.compiler_so
        if sys.platform == 'darwin':
            compiler_so = _osx_support.compiler_fixup(compiler_so, cc_args + extra_postargs)
        try:
            self.spawn(compiler_so + cc_args + [src, '-o', obj] + extra_postargs)
        except DistutilsExecError as msg:
            raise CompileError, msg

    def create_static_lib(self, objects, output_libname, output_dir=None, debug=0, target_lang=None):
        objects, output_dir = self._fix_object_args(objects, output_dir)
        output_filename = self.library_filename(output_libname, output_dir=output_dir)
        if self._need_link(objects, output_filename):
            self.mkpath(os.path.dirname(output_filename))
            self.spawn(self.archiver + [output_filename] + objects + self.objects)
            if self.ranlib:
                try:
                    self.spawn(self.ranlib + [output_filename])
                except DistutilsExecError as msg:
                    raise LibError, msg

        else:
            log.debug('skipping %s (up-to-date)', output_filename)

    def link(self, target_desc, objects, output_filename, output_dir=None, libraries=None, library_dirs=None, runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None, build_temp=None, target_lang=None):
        objects, output_dir = self._fix_object_args(objects, output_dir)
        libraries, library_dirs, runtime_library_dirs = self._fix_lib_args(libraries, library_dirs, runtime_library_dirs)
        lib_opts = gen_lib_options(self, library_dirs, runtime_library_dirs, libraries)
        if type(output_dir) not in (StringType, NoneType):
            raise TypeError, "'output_dir' must be a string or None"
        if output_dir is not None:
            output_filename = os.path.join(output_dir, output_filename)
        if self._need_link(objects, output_filename):
            ld_args = objects + self.objects + lib_opts + ['-o', output_filename]
            if debug:
                ld_args[:0] = ['-g']
            if extra_preargs:
                ld_args[:0] = extra_preargs
            if extra_postargs:
                ld_args.extend(extra_postargs)
            self.mkpath(os.path.dirname(output_filename))
            try:
                if target_desc == CCompiler.EXECUTABLE:
                    linker = self.linker_exe[:]
                else:
                    linker = self.linker_so[:]
                if target_lang == 'c++' and self.compiler_cxx:
                    i = 0
                    if os.path.basename(linker[0]) == 'env':
                        i = 1
                        while '=' in linker[i]:
                            i = i + 1

                    linker[i] = self.compiler_cxx[i]
                if sys.platform == 'darwin':
                    linker = _osx_support.compiler_fixup(linker, ld_args)
                self.spawn(linker + ld_args)
            except DistutilsExecError as msg:
                raise LinkError, msg

        else:
            log.debug('skipping %s (up-to-date)', output_filename)
        return

    def library_dir_option(self, dir):
        return '-L' + dir

    def _is_gcc(self, compiler_name):
        return 'gcc' in compiler_name or 'g++' in compiler_name

    def runtime_library_dir_option(self, dir):
        compiler = os.path.basename(sysconfig.get_config_var('CC'))
        if sys.platform[:6] == 'darwin':
            return '-L' + dir
        elif sys.platform[:5] == 'hp-ux':
            if self._is_gcc(compiler):
                return ['-Wl,+s', '-L' + dir]
            return ['+s', '-L' + dir]
        elif sys.platform[:7] == 'irix646' or sys.platform[:6] == 'osf1V5':
            return ['-rpath', dir]
        elif self._is_gcc(compiler):
            return '-Wl,-R' + dir
        else:
            return '-R' + dir

    def library_option(self, lib):
        return '-l' + lib

    def find_library_file(self, dirs, lib, debug=0):
        shared_f = self.library_filename(lib, lib_type='shared')
        dylib_f = self.library_filename(lib, lib_type='dylib')
        static_f = self.library_filename(lib, lib_type='static')
        if sys.platform == 'darwin':
            cflags = sysconfig.get_config_var('CFLAGS')
            m = re.search('-isysroot\\s+(\\S+)', cflags)
            if m is None:
                sysroot = '/'
            else:
                sysroot = m.group(1)
        for dir in dirs:
            shared = os.path.join(dir, shared_f)
            dylib = os.path.join(dir, dylib_f)
            static = os.path.join(dir, static_f)
            if sys.platform == 'darwin' and (dir.startswith('/System/') or dir.startswith('/usr/') and not dir.startswith('/usr/local/')):
                shared = os.path.join(sysroot, dir[1:], shared_f)
                dylib = os.path.join(sysroot, dir[1:], dylib_f)
                static = os.path.join(sysroot, dir[1:], static_f)
            if os.path.exists(dylib):
                return dylib
            if os.path.exists(shared):
                return shared
            if os.path.exists(static):
                return static

        return
