# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/sysconfig.py
# Compiled at: 2010-05-25 20:46:16
"""Provide access to Python's configuration information.  The specific
configuration variables available depend heavily on the platform and
configuration.  The values may be retrieved using
get_config_var(name), and the list of variables is available via
get_config_vars().keys().  Additional convenience functions are also
available.

Written by:   Fred L. Drake, Jr.
Email:        <fdrake@acm.org>
"""
__revision__ = '$Id: sysconfig.py 75023 2009-09-22 19:31:34Z ronald.oussoren $'
import os
import re
import string
import sys
from distutils.errors import DistutilsPlatformError
PREFIX = os.path.normpath(sys.prefix)
EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
project_base = os.path.dirname(os.path.abspath(sys.executable))
if os.name == 'nt' and 'pcbuild' in project_base[-8:].lower():
    project_base = os.path.abspath(os.path.join(project_base, os.path.pardir))
if os.name == 'nt' and '\\pc\\v' in project_base[-10:].lower():
    project_base = os.path.abspath(os.path.join(project_base, os.path.pardir, os.path.pardir))
if os.name == 'nt' and '\\pcbuild\\amd64' in project_base[-14:].lower():
    project_base = os.path.abspath(os.path.join(project_base, os.path.pardir, os.path.pardir))

def _python_build():
    for fn in ('Setup.dist', 'Setup.local'):
        if os.path.isfile(os.path.join(project_base, 'Modules', fn)):
            return True

    return False


python_build = _python_build()

def get_python_version():
    """Return a string containing the major and minor Python version,
    leaving off the patchlevel.  Sample return values could be '1.5'
    or '2.2'.
    """
    return sys.version[:3]


def get_python_inc(plat_specific=0, prefix=None):
    """Return the directory containing installed Python header files.
    
    If 'plat_specific' is false (the default), this is the path to the
    non-platform-specific header files, i.e. Python.h and so on;
    otherwise, this is the path to platform-specific header files
    (namely pyconfig.h).
    
    If 'prefix' is supplied, use it instead of sys.prefix or
    sys.exec_prefix -- i.e., ignore 'plat_specific'.
    """
    if prefix is None:
        if not (plat_specific and EXEC_PREFIX):
            prefix = PREFIX
        if os.name == 'posix':
            if python_build:
                base = os.path.dirname(os.path.abspath(sys.executable))
                inc_dir = plat_specific and base
            else:
                inc_dir = os.path.join(base, 'Include')
                if not os.path.exists(inc_dir):
                    inc_dir = os.path.join(os.path.dirname(base), 'Include')
            return inc_dir
        return os.path.join(prefix, 'include', 'python' + get_python_version())
    elif os.name == 'nt':
        return os.path.join(prefix, 'include')
    else:
        if os.name == 'mac':
            if plat_specific:
                return os.path.join(prefix, 'Mac', 'Include')
            else:
                return os.path.join(prefix, 'Include')
        else:
            if os.name == 'os2':
                return os.path.join(prefix, 'Include')
            raise DistutilsPlatformError("I don't know where Python installs its C header files on platform '%s'" % os.name)
        return


def get_python_lib(plat_specific=0, standard_lib=0, prefix=None):
    """Return the directory containing the Python library (standard or
    site additions).
    
    If 'plat_specific' is true, return the directory containing
    platform-specific modules, i.e. any module from a non-pure-Python
    module distribution; otherwise, return the platform-shared library
    directory.  If 'standard_lib' is true, return the directory
    containing standard Python library modules; otherwise, return the
    directory for site-specific modules.
    
    If 'prefix' is supplied, use it instead of sys.prefix or
    sys.exec_prefix -- i.e., ignore 'plat_specific'.
    """
    if prefix is None:
        if not (plat_specific and EXEC_PREFIX):
            prefix = PREFIX
        if os.name == 'posix':
            libpython = os.path.join(prefix, 'lib', 'python' + get_python_version())
            return standard_lib and libpython
        else:
            return os.path.join(libpython, 'site-packages')
    elif os.name == 'nt':
        if standard_lib:
            return os.path.join(prefix, 'Lib')
        elif get_python_version() < '2.2':
            return prefix
        else:
            return os.path.join(prefix, 'Lib', 'site-packages')
    elif os.name == 'mac':
        if plat_specific:
            if standard_lib:
                return os.path.join(prefix, 'Lib', 'lib-dynload')
            else:
                return os.path.join(prefix, 'Lib', 'site-packages')
        elif standard_lib:
            return os.path.join(prefix, 'Lib')
        else:
            return os.path.join(prefix, 'Lib', 'site-packages')

    elif os.name == 'os2':
        if standard_lib:
            return os.path.join(prefix, 'Lib')
        else:
            return os.path.join(prefix, 'Lib', 'site-packages')
    else:
        raise DistutilsPlatformError("I don't know where Python installs its library on platform '%s'" % os.name)
    return


def customize_compiler(compiler):
    """Do any platform-specific customization of a CCompiler instance.
    
    Mainly needed on Unix, so we can plug in the information that
    varies across Unices and is stored in Python's Makefile.
    """
    if compiler.compiler_type == 'unix':
        cc, cxx, opt, cflags, ccshared, ldshared, so_ext = get_config_vars('CC', 'CXX', 'OPT', 'CFLAGS', 'CCSHARED', 'LDSHARED', 'SO')
        if 'CC' in os.environ:
            cc = os.environ['CC']
        if 'CXX' in os.environ:
            cxx = os.environ['CXX']
        if 'LDSHARED' in os.environ:
            ldshared = os.environ['LDSHARED']
        if 'CPP' in os.environ:
            cpp = os.environ['CPP']
        else:
            cpp = cc + ' -E'
        if 'LDFLAGS' in os.environ:
            ldshared = ldshared + ' ' + os.environ['LDFLAGS']
        if 'CFLAGS' in os.environ:
            cflags = opt + ' ' + os.environ['CFLAGS']
            ldshared = ldshared + ' ' + os.environ['CFLAGS']
        if 'CPPFLAGS' in os.environ:
            cpp = cpp + ' ' + os.environ['CPPFLAGS']
            cflags = cflags + ' ' + os.environ['CPPFLAGS']
            ldshared = ldshared + ' ' + os.environ['CPPFLAGS']
        cc_cmd = cc + ' ' + cflags
        compiler.set_executables(preprocessor=cpp, compiler=cc_cmd, compiler_so=cc_cmd + ' ' + ccshared, compiler_cxx=cxx, linker_so=ldshared, linker_exe=cc)
        compiler.shared_lib_extension = so_ext


def get_config_h_filename():
    """Return full pathname of installed pyconfig.h file."""
    if python_build:
        if os.name == 'nt':
            inc_dir = os.path.join(project_base, 'PC')
        else:
            inc_dir = project_base
    else:
        inc_dir = get_python_inc(plat_specific=1)
    if get_python_version() < '2.2':
        config_h = 'config.h'
    else:
        config_h = 'pyconfig.h'
    return os.path.join(inc_dir, config_h)


def get_makefile_filename():
    """Return full pathname of installed Makefile from the Python build."""
    if python_build:
        return os.path.join(os.path.dirname(sys.executable), 'Makefile')
    lib_dir = get_python_lib(plat_specific=1, standard_lib=1)
    return os.path.join(lib_dir, 'config', 'Makefile')


def parse_config_h(fp, g=None):
    """Parse a config.h-style file.
    
    A dictionary containing name/value pairs is returned.  If an
    optional dictionary is passed in as the second argument, it is
    used instead of a new dictionary.
    """
    if g is None:
        g = {}
    define_rx = re.compile('#define ([A-Z][A-Za-z0-9_]+) (.*)\n')
    undef_rx = re.compile('/[*] #undef ([A-Z][A-Za-z0-9_]+) [*]/\n')
    while 1:
        line = fp.readline()
        if not line:
            break
        m = define_rx.match(line)
        if m:
            n, v = m.group(1, 2)
            try:
                v = int(v)
            except ValueError:
                pass

            g[n] = v
        else:
            m = undef_rx.match(line)
            if m:
                g[m.group(1)] = 0

    return g


_variable_rx = re.compile('([a-zA-Z][a-zA-Z0-9_]+)\\s*=\\s*(.*)')
_findvar1_rx = re.compile('\\$\\(([A-Za-z][A-Za-z0-9_]*)\\)')
_findvar2_rx = re.compile('\\${([A-Za-z][A-Za-z0-9_]*)}')

def parse_makefile--- This code section failed: ---

 268       0	LOAD_CONST        -1
           3	LOAD_CONST        ('TextFile',)
           6	IMPORT_NAME       'distutils.text_file'
           9	IMPORT_FROM       'TextFile'
          12	STORE_FAST        'TextFile'
          15	POP_TOP           ''

 269      16	LOAD_FAST         'TextFile'
          19	LOAD_FAST         'fn'
          22	LOAD_CONST        'strip_comments'
          25	LOAD_CONST        1
          28	LOAD_CONST        'skip_blanks'
          31	LOAD_CONST        1
          34	LOAD_CONST        'join_lines'
          37	LOAD_CONST        1
          40	CALL_FUNCTION_769 ''
          43	STORE_FAST        'fp'

 271      46	LOAD_FAST         'g'
          49	LOAD_CONST        ''
          52	COMPARE_OP        'is'
          55	JUMP_IF_FALSE     '67'

 272      58	BUILD_MAP         ''
          61	STORE_FAST        'g'
          64	JUMP_FORWARD      '67'
        67_0	COME_FROM         '64'

 273      67	BUILD_MAP         ''
          70	STORE_FAST        'done'

 274      73	BUILD_MAP         ''
          76	STORE_FAST        'notdone'

 276      79	SETUP_LOOP        '284'

 277      82	LOAD_FAST         'fp'
          85	LOAD_ATTR         'readline'
          88	CALL_FUNCTION_0   ''
          91	STORE_FAST        'line'

 278      94	LOAD_FAST         'line'
          97	LOAD_CONST        ''
         100	COMPARE_OP        'is'
         103	JUMP_IF_FALSE     '110'

 279     106	BREAK_LOOP        ''
         107	JUMP_FORWARD      '110'
       110_0	COME_FROM         '107'

 280     110	LOAD_GLOBAL       '_variable_rx'
         113	LOAD_ATTR         'match'
         116	LOAD_FAST         'line'
         119	CALL_FUNCTION_1   ''
         122	STORE_FAST        'm'

 281     125	LOAD_FAST         'm'
         128	JUMP_IF_FALSE     '281'

 282     131	LOAD_FAST         'm'
         134	LOAD_ATTR         'group'
         137	LOAD_CONST        1
         140	LOAD_CONST        2
         143	CALL_FUNCTION_2   ''
         146	UNPACK_SEQUENCE_2 ''
         149	STORE_FAST        'n'
         152	STORE_FAST        'v'

 283     155	LOAD_FAST         'v'
         158	LOAD_ATTR         'strip'
         161	CALL_FUNCTION_0   ''
         164	STORE_FAST        'v'

 285     167	LOAD_FAST         'v'
         170	LOAD_ATTR         'replace'
         173	LOAD_CONST        '$$'
         176	LOAD_CONST        ''
         179	CALL_FUNCTION_2   ''
         182	STORE_FAST        'tmpv'

 287     185	LOAD_CONST        '$'
         188	LOAD_FAST         'tmpv'
         191	COMPARE_OP        'in'
         194	JUMP_IF_FALSE     '210'

 288     197	LOAD_FAST         'v'
         200	LOAD_FAST         'notdone'
         203	LOAD_FAST         'n'
         206	STORE_SUBSCR      ''
         207	JUMP_ABSOLUTE     '281'

 290     210	SETUP_EXCEPT      '229'

 291     213	LOAD_GLOBAL       'int'
         216	LOAD_FAST         'v'
         219	CALL_FUNCTION_1   ''
         222	STORE_FAST        'v'
         225	POP_BLOCK         ''
         226	JUMP_FORWARD      '268'
       229_0	COME_FROM         '210'

 292     229	DUP_TOP           ''
         230	LOAD_GLOBAL       'ValueError'
         233	COMPARE_OP        'exception match'
         236	JUMP_IF_FALSE     '267'
         239	POP_TOP           ''
         240	POP_TOP           ''
         241	POP_TOP           ''

 294     242	LOAD_FAST         'v'
         245	LOAD_ATTR         'replace'
         248	LOAD_CONST        '$$'
         251	LOAD_CONST        '$'
         254	CALL_FUNCTION_2   ''
         257	LOAD_FAST         'done'
         260	LOAD_FAST         'n'
         263	STORE_SUBSCR      ''
         264	JUMP_ABSOLUTE     '281'
         267	END_FINALLY       ''
       268_0	COME_FROM         '226'

 296     268	LOAD_FAST         'v'
         271	LOAD_FAST         'done'
         274	LOAD_FAST         'n'
         277	STORE_SUBSCR      ''
       278_0	COME_FROM         '267'
         278	JUMP_BACK         '82'
         281	JUMP_BACK         '82'
       284_0	COME_FROM         '79'

 299     284	SETUP_LOOP        '637'
         287	LOAD_FAST         'notdone'
         290	JUMP_IF_FALSE     '636'

 300     293	SETUP_LOOP        '633'
         296	LOAD_FAST         'notdone'
         299	LOAD_ATTR         'keys'
         302	CALL_FUNCTION_0   ''
         305	GET_ITER          ''
         306	FOR_ITER          '632'
         309	STORE_FAST        'name'

 301     312	LOAD_FAST         'notdone'
         315	LOAD_FAST         'name'
         318	BINARY_SUBSCR     ''
         319	STORE_FAST        'value'

 302     322	LOAD_GLOBAL       '_findvar1_rx'
         325	LOAD_ATTR         'search'
         328	LOAD_FAST         'value'
         331	CALL_FUNCTION_1   ''
         334	JUMP_IF_TRUE      '349'
         337	LOAD_GLOBAL       '_findvar2_rx'
         340	LOAD_ATTR         'search'
         343	LOAD_FAST         'value'
         346	CALL_FUNCTION_1   ''
         349	STORE_FAST        'm'

 303     352	LOAD_FAST         'm'
         355	JUMP_IF_FALSE     '622'

 304     358	LOAD_FAST         'm'
         361	LOAD_ATTR         'group'
         364	LOAD_CONST        1
         367	CALL_FUNCTION_1   ''
         370	STORE_FAST        'n'

 305     373	LOAD_GLOBAL       'True'
         376	STORE_FAST        'found'

 306     379	LOAD_FAST         'n'
         382	LOAD_FAST         'done'
         385	COMPARE_OP        'in'
         388	JUMP_IF_FALSE     '410'

 307     391	LOAD_GLOBAL       'str'
         394	LOAD_FAST         'done'
         397	LOAD_FAST         'n'
         400	BINARY_SUBSCR     ''
         401	CALL_FUNCTION_1   ''
         404	STORE_FAST        'item'
         407	JUMP_FORWARD      '476'

 308     410	LOAD_FAST         'n'
         413	LOAD_FAST         'notdone'
         416	COMPARE_OP        'in'
         419	JUMP_IF_FALSE     '431'

 310     422	LOAD_GLOBAL       'False'
         425	STORE_FAST        'found'
         428	JUMP_FORWARD      '476'

 311     431	LOAD_FAST         'n'
         434	LOAD_GLOBAL       'os'
         437	LOAD_ATTR         'environ'
         440	COMPARE_OP        'in'
         443	JUMP_IF_FALSE     '462'

 313     446	LOAD_GLOBAL       'os'
         449	LOAD_ATTR         'environ'
         452	LOAD_FAST         'n'
         455	BINARY_SUBSCR     ''
         456	STORE_FAST        'item'
         459	JUMP_FORWARD      '476'

 315     462	LOAD_CONST        ''
         465	DUP_TOP           ''
         466	LOAD_FAST         'done'
         469	LOAD_FAST         'n'
         472	STORE_SUBSCR      ''
         473	STORE_FAST        'item'
       476_0	COME_FROM         '407'
       476_1	COME_FROM         '428'
       476_2	COME_FROM         '459'

 316     476	LOAD_FAST         'found'
         479	JUMP_IF_FALSE     '619'

 317     482	LOAD_FAST         'value'
         485	LOAD_FAST         'm'
         488	LOAD_ATTR         'end'
         491	CALL_FUNCTION_0   ''
         494	SLICE+1           ''
         495	STORE_FAST        'after'

 318     498	LOAD_FAST         'value'
         501	LOAD_FAST         'm'
         504	LOAD_ATTR         'start'
         507	CALL_FUNCTION_0   ''
         510	SLICE+2           ''
         511	LOAD_FAST         'item'
         514	BINARY_ADD        ''
         515	LOAD_FAST         'after'
         518	BINARY_ADD        ''
         519	STORE_FAST        'value'

 319     522	LOAD_CONST        '$'
         525	LOAD_FAST         'after'
         528	COMPARE_OP        'in'
         531	JUMP_IF_FALSE     '547'

 320     534	LOAD_FAST         'value'
         537	LOAD_FAST         'notdone'
         540	LOAD_FAST         'name'
         543	STORE_SUBSCR      ''
         544	JUMP_ABSOLUTE     '619'

 322     547	SETUP_EXCEPT      '566'
         550	LOAD_GLOBAL       'int'
         553	LOAD_FAST         'value'
         556	CALL_FUNCTION_1   ''
         559	STORE_FAST        'value'
         562	POP_BLOCK         ''
         563	JUMP_FORWARD      '599'
       566_0	COME_FROM         '547'

 323     566	DUP_TOP           ''
         567	LOAD_GLOBAL       'ValueError'
         570	COMPARE_OP        'exception match'
         573	JUMP_IF_FALSE     '598'
         576	POP_TOP           ''
         577	POP_TOP           ''
         578	POP_TOP           ''

 324     579	LOAD_FAST         'value'
         582	LOAD_ATTR         'strip'
         585	CALL_FUNCTION_0   ''
         588	LOAD_FAST         'done'
         591	LOAD_FAST         'name'
         594	STORE_SUBSCR      ''
         595	JUMP_FORWARD      '609'
         598	END_FINALLY       ''
       599_0	COME_FROM         '563'

 326     599	LOAD_FAST         'value'
         602	LOAD_FAST         'done'
         605	LOAD_FAST         'name'
         608	STORE_SUBSCR      ''
       609_0	COME_FROM         '598'

 327     609	LOAD_FAST         'notdone'
         612	LOAD_FAST         'name'
         615	DELETE_SUBSCR     ''
         616	JUMP_ABSOLUTE     '629'
         619	JUMP_BACK         '306'

 330     622	LOAD_FAST         'notdone'
         625	LOAD_FAST         'name'
         628	DELETE_SUBSCR     ''
         629	JUMP_BACK         '306'
         632	POP_BLOCK         ''
       633_0	COME_FROM         '293'
         633	JUMP_BACK         '287'
         636	POP_BLOCK         ''
       637_0	COME_FROM         '284'

 332     637	LOAD_FAST         'fp'
         640	LOAD_ATTR         'close'
         643	CALL_FUNCTION_0   ''
         646	POP_TOP           ''

 335     647	LOAD_FAST         'g'
         650	LOAD_ATTR         'update'
         653	LOAD_FAST         'done'
         656	CALL_FUNCTION_1   ''
         659	POP_TOP           ''

 336     660	LOAD_FAST         'g'
         663	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 636


def expand_makefile_vars(s, vars):
    """Expand Makefile-style variables -- "${foo}" or "$(foo)" -- in
    'string' according to 'vars' (a dictionary mapping variable names to
    values).  Variables not present in 'vars' are silently expanded to the
    empty string.  The variable values in 'vars' should not contain further
    variable expansions; if 'vars' is the output of 'parse_makefile()',
    you're fine.  Returns a variable-expanded version of 's'.
    """
    while 1:
        if not _findvar1_rx.search(s):
            m = _findvar2_rx.search(s)
            beg, end = m and m.span()
            s = s[0:beg] + vars.get(m.group(1)) + s[end:]
        else:
            break

    return s


_config_vars = None

def _init_posix():
    """Initialize the module as appropriate for POSIX systems."""
    global _config_vars
    g = {}
    try:
        filename = get_makefile_filename()
        parse_makefile(filename, g)
    except IOError as msg:
        my_msg = 'invalid Python installation: unable to open %s' % filename
        if hasattr(msg, 'strerror'):
            my_msg = my_msg + ' (%s)' % msg.strerror
        raise DistutilsPlatformError(my_msg)

    try:
        filename = get_config_h_filename()
        parse_config_h(file(filename), g)
    except IOError as msg:
        my_msg = 'invalid Python installation: unable to open %s' % filename
        if hasattr(msg, 'strerror'):
            my_msg = my_msg + ' (%s)' % msg.strerror
        raise DistutilsPlatformError(my_msg)

    if sys.platform == 'darwin' and 'MACOSX_DEPLOYMENT_TARGET' in g:
        cfg_target = g['MACOSX_DEPLOYMENT_TARGET']
        cur_target = os.getenv('MACOSX_DEPLOYMENT_TARGET', '')
        if cur_target == '':
            cur_target = cfg_target
            os.putenv('MACOSX_DEPLOYMENT_TARGET', cfg_target)
        elif map(int, cfg_target.split('.')) > map(int, cur_target.split('.')):
            my_msg = '$MACOSX_DEPLOYMENT_TARGET mismatch: now "%s" but "%s" during configure' % (cur_target, cfg_target)
            raise DistutilsPlatformError(my_msg)
    if python_build:
        g['LDSHARED'] = g['BLDSHARED']
    elif get_python_version() < '2.1':
        if sys.platform == 'aix4':
            python_lib = get_python_lib(standard_lib=1)
            ld_so_aix = os.path.join(python_lib, 'config', 'ld_so_aix')
            python_exp = os.path.join(python_lib, 'config', 'python.exp')
            g['LDSHARED'] = '%s %s -bI:%s' % (ld_so_aix, g['CC'], python_exp)
        elif sys.platform == 'beos':
            python_lib = get_python_lib(standard_lib=1)
            linkerscript_path = string.split(g['LDSHARED'])[0]
            linkerscript_name = os.path.basename(linkerscript_path)
            linkerscript = os.path.join(python_lib, 'config', linkerscript_name)
            g['LDSHARED'] = '%s -L%s/lib -lpython%s' % (linkerscript, PREFIX, get_python_version())
    _config_vars = g


def _init_nt():
    """Initialize the module as appropriate for NT"""
    global _config_vars
    g = {}
    g['LIBDEST'] = get_python_lib(plat_specific=0, standard_lib=1)
    g['BINLIBDEST'] = get_python_lib(plat_specific=1, standard_lib=1)
    g['INCLUDEPY'] = get_python_inc(plat_specific=0)
    g['SO'] = '.pyd'
    g['EXE'] = '.exe'
    g['VERSION'] = get_python_version().replace('.', '')
    g['BINDIR'] = os.path.dirname(os.path.abspath(sys.executable))
    _config_vars = g


def _init_mac():
    """Initialize the module as appropriate for Macintosh systems"""
    global _config_vars
    g = {}
    g['LIBDEST'] = get_python_lib(plat_specific=0, standard_lib=1)
    g['BINLIBDEST'] = get_python_lib(plat_specific=1, standard_lib=1)
    g['INCLUDEPY'] = get_python_inc(plat_specific=0)
    import MacOS
    if not hasattr(MacOS, 'runtimemodel'):
        g['SO'] = '.ppc.slb'
    else:
        g['SO'] = '.%s.slb' % MacOS.runtimemodel
    g['install_lib'] = os.path.join(EXEC_PREFIX, 'Lib')
    g['install_platlib'] = os.path.join(EXEC_PREFIX, 'Mac', 'Lib')
    g['srcdir'] = ':'
    _config_vars = g


def _init_os2():
    """Initialize the module as appropriate for OS/2"""
    global _config_vars
    g = {}
    g['LIBDEST'] = get_python_lib(plat_specific=0, standard_lib=1)
    g['BINLIBDEST'] = get_python_lib(plat_specific=1, standard_lib=1)
    g['INCLUDEPY'] = get_python_inc(plat_specific=0)
    g['SO'] = '.pyd'
    g['EXE'] = '.exe'
    _config_vars = g


def get_config_vars(*args):
    """With no arguments, return a dictionary of all configuration
    variables relevant for the current platform.  Generally this includes
    everything needed to build extensions and install both pure modules and
    extensions.  On Unix, this means every variable defined in Python's
    installed Makefile; on Windows and Mac OS it's a much smaller set.
    
    With arguments, return a list of values that result from looking up
    each argument in the configuration variable dictionary.
    """
    global _config_vars
    if _config_vars is None:
        func = globals().get('_init_' + os.name)
        if func:
            func()
        else:
            _config_vars = {}
        _config_vars['prefix'] = PREFIX
        _config_vars['exec_prefix'] = EXEC_PREFIX
        if sys.platform == 'darwin':
            kernel_version = os.uname()[2]
            major_version = int(kernel_version.split('.')[0])
            if major_version < 8:
                for key in ('LDFLAGS', 'BASECFLAGS', 'CFLAGS', 'PY_CFLAGS', 'BLDSHARED'):
                    flags = _config_vars[key]
                    flags = re.sub('-arch\\s+\\w+\\s', ' ', flags)
                    flags = re.sub('-isysroot [^ \t]*', ' ', flags)
                    _config_vars[key] = flags

            else:
                if 'ARCHFLAGS' in os.environ:
                    arch = os.environ['ARCHFLAGS']
                    for key in ('LDFLAGS', 'BASECFLAGS', 'CFLAGS', 'PY_CFLAGS', 'BLDSHARED'):
                        flags = _config_vars[key]
                        flags = re.sub('-arch\\s+\\w+\\s', ' ', flags)
                        flags = flags + ' ' + arch
                        _config_vars[key] = flags

                m = re.search('-isysroot\\s+(\\S+)', _config_vars['CFLAGS'])
                if m is not None:
                    sdk = m.group(1)
                    if not os.path.exists(sdk):
                        for key in ('LDFLAGS', 'BASECFLAGS', 'CFLAGS', 'PY_CFLAGS', 'BLDSHARED'):
                            flags = _config_vars[key]
                            flags = re.sub('-isysroot\\s+\\S+(\\s|$)', ' ', flags)
                            _config_vars[key] = flags

    if args:
        vals = []
        for name in args:
            vals.append(_config_vars.get(name))

        return vals
    else:
        return _config_vars
        return


def get_config_var(name):
    """Return the value of a single variable using the dictionary
    returned by 'get_config_vars()'.  Equivalent to
    get_config_vars().get(name)
    """
    return get_config_vars().get(name)