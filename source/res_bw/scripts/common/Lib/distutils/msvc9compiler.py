# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/msvc9compiler.py
# Compiled at: 2010-10-21 18:49:01
"""distutils.msvc9compiler

Contains MSVCCompiler, an implementation of the abstract CCompiler class
for the Microsoft Visual Studio 2008.

The module is compatible with VS 2005 and VS 2008. You can find legacy support
for older versions of VS in distutils.msvccompiler.
"""
__revision__ = '$Id: msvc9compiler.py 68082 2008-12-30 23:06:46Z tarek.ziade $'
import os
import subprocess
import sys
from distutils.errors import DistutilsExecError, DistutilsPlatformError, CompileError, LibError, LinkError
from distutils.ccompiler import CCompiler, gen_preprocess_options, gen_lib_options
from distutils import log
from distutils.util import get_platform
import _winreg
RegOpenKeyEx = _winreg.OpenKeyEx
RegEnumKey = _winreg.EnumKey
RegEnumValue = _winreg.EnumValue
RegError = _winreg.error
HKEYS = (_winreg.HKEY_USERS,
 _winreg.HKEY_CURRENT_USER,
 _winreg.HKEY_LOCAL_MACHINE,
 _winreg.HKEY_CLASSES_ROOT)
VS_BASE = 'Software\\Microsoft\\VisualStudio\\%0.1f'
WINSDK_BASE = 'Software\\Microsoft\\Microsoft SDKs\\Windows'
NET_BASE = 'Software\\Microsoft\\.NETFramework'
PLAT_TO_VCVARS = {'win32': 'x86',
 'win-amd64': 'amd64',
 'win-ia64': 'ia64'}

class Reg:
    """Helper class to read values from the registry
    """

    @classmethod
    def get_value(cls, path, key):
        for base in HKEYS:
            d = cls.read_values(base, path)
            if d and key in d:
                return d[key]

        raise KeyError(key)

    @classmethod
    def read_keys--- This code section failed: ---

  67       0	SETUP_EXCEPT      '22'

  68       3	LOAD_GLOBAL       'RegOpenKeyEx'
           6	LOAD_FAST         'base'
           9	LOAD_FAST         'key'
          12	CALL_FUNCTION_2   ''
          15	STORE_FAST        'handle'
          18	POP_BLOCK         ''
          19	JUMP_FORWARD      '40'
        22_0	COME_FROM         '0'

  69      22	DUP_TOP           ''
          23	LOAD_GLOBAL       'RegError'
          26	COMPARE_OP        'exception match'
          29	JUMP_IF_FALSE     '39'
          32	POP_TOP           ''
          33	POP_TOP           ''
          34	POP_TOP           ''

  70      35	LOAD_CONST        ''
          38	RETURN_VALUE      ''
          39	END_FINALLY       ''
        40_0	COME_FROM         '19'
        40_1	COME_FROM         '39'

  71      40	BUILD_LIST_0      ''
          43	STORE_FAST        'L'

  72      46	LOAD_CONST        0
          49	STORE_FAST        'i'

  73      52	SETUP_LOOP        '128'
          55	LOAD_GLOBAL       'True'
          58	JUMP_IF_FALSE     '127'

  74      61	SETUP_EXCEPT      '83'

  75      64	LOAD_GLOBAL       'RegEnumKey'
          67	LOAD_FAST         'handle'
          70	LOAD_FAST         'i'
          73	CALL_FUNCTION_2   ''
          76	STORE_FAST        'k'
          79	POP_BLOCK         ''
          80	JUMP_FORWARD      '101'
        83_0	COME_FROM         '61'

  76      83	DUP_TOP           ''
          84	LOAD_GLOBAL       'RegError'
          87	COMPARE_OP        'exception match'
          90	JUMP_IF_FALSE     '100'
          93	POP_TOP           ''
          94	POP_TOP           ''
          95	POP_TOP           ''

  77      96	BREAK_LOOP        ''
          97	JUMP_FORWARD      '101'
         100	END_FINALLY       ''
       101_0	COME_FROM         '80'
       101_1	COME_FROM         '100'

  78     101	LOAD_FAST         'L'
         104	LOAD_ATTR         'append'
         107	LOAD_FAST         'k'
         110	CALL_FUNCTION_1   ''
         113	POP_TOP           ''

  79     114	LOAD_FAST         'i'
         117	LOAD_CONST        1
         120	INPLACE_ADD       ''
         121	STORE_FAST        'i'
         124	JUMP_BACK         '55'
         127	POP_BLOCK         ''
       128_0	COME_FROM         '52'

  80     128	LOAD_FAST         'L'
         131	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 127

    @classmethod
    def read_values--- This code section failed: ---

  88       0	SETUP_EXCEPT      '22'

  89       3	LOAD_GLOBAL       'RegOpenKeyEx'
           6	LOAD_FAST         'base'
           9	LOAD_FAST         'key'
          12	CALL_FUNCTION_2   ''
          15	STORE_FAST        'handle'
          18	POP_BLOCK         ''
          19	JUMP_FORWARD      '40'
        22_0	COME_FROM         '0'

  90      22	DUP_TOP           ''
          23	LOAD_GLOBAL       'RegError'
          26	COMPARE_OP        'exception match'
          29	JUMP_IF_FALSE     '39'
          32	POP_TOP           ''
          33	POP_TOP           ''
          34	POP_TOP           ''

  91      35	LOAD_CONST        ''
          38	RETURN_VALUE      ''
          39	END_FINALLY       ''
        40_0	COME_FROM         '19'
        40_1	COME_FROM         '39'

  92      40	BUILD_MAP         ''
          43	STORE_FAST        'd'

  93      46	LOAD_CONST        0
          49	STORE_FAST        'i'

  94      52	SETUP_LOOP        '164'
          55	LOAD_GLOBAL       'True'
          58	JUMP_IF_FALSE     '163'

  95      61	SETUP_EXCEPT      '92'

  96      64	LOAD_GLOBAL       'RegEnumValue'
          67	LOAD_FAST         'handle'
          70	LOAD_FAST         'i'
          73	CALL_FUNCTION_2   ''
          76	UNPACK_SEQUENCE_3 ''
          79	STORE_FAST        'name'
          82	STORE_FAST        'value'
          85	STORE_FAST        'type'
          88	POP_BLOCK         ''
          89	JUMP_FORWARD      '110'
        92_0	COME_FROM         '61'

  97      92	DUP_TOP           ''
          93	LOAD_GLOBAL       'RegError'
          96	COMPARE_OP        'exception match'
          99	JUMP_IF_FALSE     '109'
         102	POP_TOP           ''
         103	POP_TOP           ''
         104	POP_TOP           ''

  98     105	BREAK_LOOP        ''
         106	JUMP_FORWARD      '110'
         109	END_FINALLY       ''
       110_0	COME_FROM         '89'
       110_1	COME_FROM         '109'

  99     110	LOAD_FAST         'name'
         113	LOAD_ATTR         'lower'
         116	CALL_FUNCTION_0   ''
         119	STORE_FAST        'name'

 100     122	LOAD_FAST         'cls'
         125	LOAD_ATTR         'convert_mbcs'
         128	LOAD_FAST         'value'
         131	CALL_FUNCTION_1   ''
         134	LOAD_FAST         'd'
         137	LOAD_FAST         'cls'
         140	LOAD_ATTR         'convert_mbcs'
         143	LOAD_FAST         'name'
         146	CALL_FUNCTION_1   ''
         149	STORE_SUBSCR      ''

 101     150	LOAD_FAST         'i'
         153	LOAD_CONST        1
         156	INPLACE_ADD       ''
         157	STORE_FAST        'i'
         160	JUMP_BACK         '55'
         163	POP_BLOCK         ''
       164_0	COME_FROM         '52'

 102     164	LOAD_FAST         'd'
         167	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 163

    @staticmethod
    def convert_mbcs(s):
        dec = getattr(s, 'decode', None)
        if dec is not None:
            try:
                s = dec('mbcs')
            except UnicodeError:
                pass

        return s


class MacroExpander:

    def __init__(self, version):
        self.macros = {}
        self.vsbase = VS_BASE % version
        self.load_macros(version)

    def set_macro(self, macro, path, key):
        self.macros['$(%s)' % macro] = Reg.get_value(path, key)

    def load_macros(self, version):
        self.set_macro('VCInstallDir', self.vsbase + '\\Setup\\VC', 'productdir')
        self.set_macro('VSInstallDir', self.vsbase + '\\Setup\\VS', 'productdir')
        self.set_macro('FrameworkDir', NET_BASE, 'installroot')
        try:
            if version >= 8.0:
                self.set_macro('FrameworkSDKDir', NET_BASE, 'sdkinstallrootv2.0')
            else:
                raise KeyError('sdkinstallrootv2.0')
        except KeyError as exc:
            raise DistutilsPlatformError('Python was built with Visual Studio 2008;\nextensions must be built with a compiler than can generate compatible binaries.\nVisual Studio 2008 was not found on this system. If you have Cygwin installed,\nyou can try compiling with MingW32, by passing "-c mingw32" to setup.py.')

        if version >= 9.0:
            self.set_macro('FrameworkVersion', self.vsbase, 'clr version')
            self.set_macro('WindowsSdkDir', WINSDK_BASE, 'currentinstallfolder')
        else:
            p = 'Software\\Microsoft\\NET Framework Setup\\Product'
            for base in HKEYS:
                try:
                    h = RegOpenKeyEx(base, p)
                except RegError:
                    continue

                key = RegEnumKey(h, 0)
                d = Reg.get_value(base, '%s\\%s' % (p, key))
                self.macros['$(FrameworkVersion)'] = d['version']

    def sub(self, s):
        for k, v in self.macros.items():
            s = s.replace(k, v)

        return s


def get_build_version():
    """Return the version of MSVC that was used to build Python.
    
    For Python 2.3 and up, the version number is included in
    sys.version.  For earlier versions, assume the compiler is MSVC 6.
    """
    prefix = 'MSC v.'
    i = sys.version.find(prefix)
    if i == -1:
        return 6
    i = i + len(prefix)
    s, rest = sys.version[i:].split(' ', 1)
    majorVersion = int(s[:-2]) - 6
    minorVersion = int(s[2:3]) / 10.0
    if majorVersion == 6:
        minorVersion = 0
    if majorVersion >= 6:
        return majorVersion + minorVersion
    else:
        return None


def normalize_and_reduce_paths(paths):
    """Return a list of normalized paths with duplicates removed.
    
    The current order of paths is maintained.
    """
    reduced_paths = []
    for p in paths:
        np = os.path.normpath(p)
        if np not in reduced_paths:
            reduced_paths.append(np)

    return reduced_paths


def removeDuplicates(variable):
    """Remove duplicate values of an environment variable.
    """
    oldList = variable.split(os.pathsep)
    newList = []
    for i in oldList:
        if i not in newList:
            newList.append(i)

    newVariable = os.pathsep.join(newList)
    return newVariable


def find_vcvarsall(version):
    """Find the vcvarsall.bat file
    
    At first it tries to find the productdir of VS 2008 in the registry. If
    that fails it falls back to the VS90COMNTOOLS env var.
    """
    vsbase = VS_BASE % version
    try:
        productdir = Reg.get_value('%s\\Setup\\VC' % vsbase, 'productdir')
    except KeyError:
        log.debug('Unable to find productdir in registry')
        productdir = None

    if not productdir or not os.path.isdir(productdir):
        toolskey = 'VS%0.f0COMNTOOLS' % version
        toolsdir = os.environ.get(toolskey, None)
        if toolsdir and os.path.isdir(toolsdir):
            productdir = os.path.join(toolsdir, os.pardir, os.pardir, 'VC')
            productdir = os.path.abspath(productdir)
            if not os.path.isdir(productdir):
                log.debug('%s is not a valid directory' % productdir)
                return
        else:
            log.debug('Env var %s is not set or invalid' % toolskey)
    if not productdir:
        log.debug('No productdir found')
        return
    else:
        vcvarsall = os.path.join(productdir, 'vcvarsall.bat')
        if os.path.isfile(vcvarsall):
            return vcvarsall
        log.debug('Unable to find vcvarsall.bat')
        return


def query_vcvarsall(version, arch='x86'):
    """Launch vcvarsall.bat and read the settings from its environment
    """
    vcvarsall = find_vcvarsall(version)
    interesting = set(('include', 'lib', 'libpath', 'path'))
    result = {}
    if vcvarsall is None:
        raise DistutilsPlatformError('Unable to find vcvarsall.bat')
    log.debug("Calling 'vcvarsall.bat %s' (version=%s)", arch, version)
    popen = subprocess.Popen('"%s" %s & set' % (vcvarsall, arch), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    if popen.wait() != 0:
        raise DistutilsPlatformError(stderr.decode('mbcs'))
    stdout = stdout.decode('mbcs')
    for line in stdout.split('\n'):
        line = Reg.convert_mbcs(line)
        if '=' not in line:
            continue
        line = line.strip()
        key, value = line.split('=', 1)
        key = key.lower()
        if key in interesting:
            if value.endswith(os.pathsep):
                value = value[:-1]
            result[key] = removeDuplicates(value)

    if len(result) != len(interesting):
        raise ValueError(str(list(result.keys())))
    return result


VERSION = get_build_version()
if VERSION < 8.0:
    raise DistutilsPlatformError('VC %0.1f is not supported by this module' % VERSION)

class MSVCCompiler(CCompiler):
    """Concrete class that implements an interface to Microsoft Visual C++,
    as defined by the CCompiler abstract class."""
    compiler_type = 'msvc'
    executables = {}
    _c_extensions = ['.c']
    _cpp_extensions = ['.cc', '.cpp', '.cxx']
    _rc_extensions = ['.rc']
    _mc_extensions = ['.mc']
    src_extensions = _c_extensions + _cpp_extensions + _rc_extensions + _mc_extensions
    res_extension = '.res'
    obj_extension = '.obj'
    static_lib_extension = '.lib'
    shared_lib_extension = '.dll'
    static_lib_format = shared_lib_format = '%s%s'
    exe_extension = '.exe'

    def __init__(self, verbose=0, dry_run=0, force=0):
        CCompiler.__init__(self, verbose, dry_run, force)
        self.__version = VERSION
        self.__root = 'Software\\Microsoft\\VisualStudio'
        self.__paths = []
        self.plat_name = None
        self.__arch = None
        self.initialized = False
        return

    def initialize(self, plat_name=None):
        assert not self.initialized, "don't init multiple times"
        if plat_name is None:
            plat_name = get_platform()
        ok_plats = ('win32', 'win-amd64', 'win-ia64')
        if plat_name not in ok_plats:
            raise DistutilsPlatformError('--plat-name must be one of %s' % (ok_plats,))
        if 'DISTUTILS_USE_SDK' in os.environ and 'MSSdk' in os.environ and self.find_exe('cl.exe'):
            self.cc = 'cl.exe'
            self.linker = 'link.exe'
            self.lib = 'lib.exe'
            self.rc = 'rc.exe'
            self.mc = 'mc.exe'
        else:
            if plat_name == get_platform() or plat_name == 'win32':
                plat_spec = PLAT_TO_VCVARS[plat_name]
            else:
                plat_spec = PLAT_TO_VCVARS[get_platform()] + '_' + PLAT_TO_VCVARS[plat_name]
            vc_env = query_vcvarsall(VERSION, plat_spec)
            self.__paths = vc_env['path'].encode('mbcs').split(os.pathsep)
            os.environ['lib'] = vc_env['lib'].encode('mbcs')
            os.environ['include'] = vc_env['include'].encode('mbcs')
            if len(self.__paths) == 0:
                raise DistutilsPlatformError("Python was built with %s, and extensions need to be built with the same version of the compiler, but it isn't installed." % self.__product)
            self.cc = self.find_exe('cl.exe')
            self.linker = self.find_exe('link.exe')
            self.lib = self.find_exe('lib.exe')
            self.rc = self.find_exe('rc.exe')
            self.mc = self.find_exe('mc.exe')
        try:
            for p in os.environ['path'].split(';'):
                self.__paths.append(p)

        except KeyError:
            pass

        self.__paths = normalize_and_reduce_paths(self.__paths)
        os.environ['path'] = ';'.join(self.__paths)
        self.preprocess_options = None
        if self.__arch == 'x86':
            self.compile_options = ['/nologo',
             '/Ox',
             '/MD',
             '/W3',
             '/DNDEBUG']
            self.compile_options_debug = ['/nologo',
             '/Od',
             '/MDd',
             '/W3',
             '/Z7',
             '/D_DEBUG']
        else:
            self.compile_options = ['/nologo',
             '/Ox',
             '/MD',
             '/W3',
             '/GS-',
             '/DNDEBUG']
            self.compile_options_debug = ['/nologo',
             '/Od',
             '/MDd',
             '/W3',
             '/GS-',
             '/Z7',
             '/D_DEBUG']
        self.ldflags_shared = ['/DLL', '/nologo', '/INCREMENTAL:NO']
        if self.__version >= 7:
            self.ldflags_shared_debug = ['/DLL',
             '/nologo',
             '/INCREMENTAL:no',
             '/DEBUG',
             '/pdb:None']
        self.ldflags_static = ['/nologo']
        self.initialized = True
        return

    def object_filenames(self, source_filenames, strip_dir=0, output_dir=''):
        if output_dir is None:
            output_dir = ''
        obj_names = []
        for src_name in source_filenames:
            base, ext = os.path.splitext(src_name)
            base = os.path.splitdrive(base)[1]
            base = base[os.path.isabs(base):]
            if ext not in self.src_extensions:
                raise CompileError("Don't know how to compile %s" % src_name)
            if strip_dir:
                base = os.path.basename(base)
            if ext in self._rc_extensions:
                obj_names.append(os.path.join(output_dir, base + self.res_extension))
            elif ext in self._mc_extensions:
                obj_names.append(os.path.join(output_dir, base + self.res_extension))
            else:
                obj_names.append(os.path.join(output_dir, base + self.obj_extension))

        return obj_names

    def compile(self, sources, output_dir=None, macros=None, include_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, depends=None):
        if not self.initialized:
            self.initialize()
        compile_info = self._setup_compile(output_dir, macros, include_dirs, sources, depends, extra_postargs)
        macros, objects, extra_postargs, pp_opts, build = compile_info
        if not extra_preargs:
            compile_opts = []
            compile_opts.append('/c')
            debug and compile_opts.extend(self.compile_options_debug)
        else:
            compile_opts.extend(self.compile_options)
        for obj in objects:
            try:
                src, ext = build[obj]
            except KeyError:
                continue

            if debug:
                src = os.path.abspath(src)
            if ext in self._c_extensions:
                input_opt = '/Tc' + src
            elif ext in self._cpp_extensions:
                input_opt = '/Tp' + src
            elif ext in self._rc_extensions:
                input_opt = src
                output_opt = '/fo' + obj
                try:
                    self.spawn([self.rc] + pp_opts + [output_opt] + [input_opt])
                except DistutilsExecError as msg:
                    raise CompileError(msg)

                continue
            elif ext in self._mc_extensions:
                h_dir = os.path.dirname(src)
                rc_dir = os.path.dirname(obj)
                try:
                    self.spawn([self.mc] + ['-h',
                     h_dir,
                     '-r',
                     rc_dir] + [src])
                    base, _ = os.path.splitext(os.path.basename(src))
                    rc_file = os.path.join(rc_dir, base + '.rc')
                    self.spawn([self.rc] + ['/fo' + obj] + [rc_file])
                except DistutilsExecError as msg:
                    raise CompileError(msg)

                continue
            else:
                raise CompileError("Don't know how to compile %s to %s" % (src, obj))
            output_opt = '/Fo' + obj
            try:
                self.spawn([self.cc] + compile_opts + pp_opts + [input_opt, output_opt] + extra_postargs)
            except DistutilsExecError as msg:
                raise CompileError(msg)

        return objects

    def create_static_lib(self, objects, output_libname, output_dir=None, debug=0, target_lang=None):
        if not self.initialized:
            self.initialize()
        objects, output_dir = self._fix_object_args(objects, output_dir)
        output_filename = self.library_filename(output_libname, output_dir=output_dir)
        if self._need_link(objects, output_filename):
            lib_args = objects + ['/OUT:' + output_filename]
            if debug:
                pass
            try:
                self.spawn([self.lib] + lib_args)
            except DistutilsExecError as msg:
                raise LibError(msg)

        else:
            log.debug('skipping %s (up-to-date)', output_filename)

    def link(self, target_desc, objects, output_filename, output_dir=None, libraries=None, library_dirs=None, runtime_library_dirs=None, export_symbols=None, debug=0, extra_preargs=None, extra_postargs=None, build_temp=None, target_lang=None):
        if not self.initialized:
            self.initialize()
        objects, output_dir = self._fix_object_args(objects, output_dir)
        fixed_args = self._fix_lib_args(libraries, library_dirs, runtime_library_dirs)
        libraries, library_dirs, runtime_library_dirs = fixed_args
        if runtime_library_dirs:
            self.warn("I don't know what to do with 'runtime_library_dirs': " + str(runtime_library_dirs))
        lib_opts = gen_lib_options(self, library_dirs, runtime_library_dirs, libraries)
        if output_dir is not None:
            output_filename = os.path.join(output_dir, output_filename)
        if self._need_link(objects, output_filename):
            if target_desc == CCompiler.EXECUTABLE:
                if debug:
                    ldflags = self.ldflags_shared_debug[1:]
                else:
                    ldflags = self.ldflags_shared[1:]
            elif debug:
                ldflags = self.ldflags_shared_debug
            else:
                ldflags = self.ldflags_shared
            export_opts = []
            for sym in export_symbols or []:
                export_opts.append('/EXPORT:' + sym)

            ld_args = ldflags + lib_opts + export_opts + objects + ['/OUT:' + output_filename]
            build_temp = os.path.dirname(objects[0])
            if export_symbols is not None:
                dll_name, dll_ext = os.path.splitext(os.path.basename(output_filename))
                implib_file = os.path.join(build_temp, self.library_filename(dll_name))
                ld_args.append('/IMPLIB:' + implib_file)
            temp_manifest = os.path.join(build_temp, os.path.basename(output_filename) + '.manifest')
            ld_args.append('/MANIFESTFILE:' + temp_manifest)
            if extra_preargs:
                ld_args[:0] = extra_preargs
            if extra_postargs:
                ld_args.extend(extra_postargs)
            self.mkpath(os.path.dirname(output_filename))
            try:
                self.spawn([self.linker] + ld_args)
            except DistutilsExecError as msg:
                raise LinkError(msg)

            mfid = 1 if target_desc == CCompiler.EXECUTABLE else 2
            out_arg = '-outputresource:%s;%s' % (output_filename, mfid)
            try:
                self.spawn(['mt.exe',
                 '-nologo',
                 '-manifest',
                 temp_manifest,
                 out_arg])
            except DistutilsExecError as msg:
                raise LinkError(msg)

        else:
            log.debug('skipping %s (up-to-date)', output_filename)
        return

    def library_dir_option(self, dir):
        return '/LIBPATH:' + dir

    def runtime_library_dir_option(self, dir):
        raise DistutilsPlatformError("don't know how to set runtime library search path for MSVC++")

    def library_option(self, lib):
        return self.library_filename(lib)

    def find_library_file(self, dirs, lib, debug=0):
        if debug:
            try_names = [lib + '_d', lib]
        else:
            try_names = [lib]
        for dir in dirs:
            for name in try_names:
                libfile = os.path.join(dir, self.library_filename(name))
                if os.path.exists(libfile):
                    return libfile

        else:
            return None

        return None

    def find_exe(self, exe):
        """Return path to an MSVC executable program.
        
        Tries to find the program in several places: first, one of the
        MSVC program search paths from the registry; next, the directories
        in the PATH environment variable.  If any of those work, return an
        absolute path that is known to exist.  If none of them work, just
        return the original program name, 'exe'.
        """
        for p in self.__paths:
            fn = os.path.join(os.path.abspath(p), exe)
            if os.path.isfile(fn):
                return fn

        for p in os.environ['Path'].split(';'):
            fn = os.path.join(os.path.abspath(p), exe)
            if os.path.isfile(fn):
                return fn

        return exe