# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/_osx_support.py
import os
import re
import sys
__all__ = ['compiler_fixup',
 'customize_config_vars',
 'customize_compiler',
 'get_platform_osx']
_UNIVERSAL_CONFIG_VARS = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS', 'BASECFLAGS', 'BLDSHARED', 'LDSHARED', 'CC', 'CXX', 'PY_CFLAGS', 'PY_LDFLAGS', 'PY_CPPFLAGS', 'PY_CORE_CFLAGS')
_COMPILER_CONFIG_VARS = ('BLDSHARED', 'LDSHARED', 'CC', 'CXX')
_INITPRE = '_OSX_SUPPORT_INITIAL_'

def _find_executable(executable, path=None):
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    base, ext = os.path.splitext(executable)
    if (sys.platform == 'win32' or os.name == 'os2') and ext != '.exe':
        executable = executable + '.exe'
    if not os.path.isfile(executable):
        for p in paths:
            f = os.path.join(p, executable)
            if os.path.isfile(f):
                return f

        return
    else:
        return executable
        return


def _read_output(commandstring):
    import contextlib
    try:
        import tempfile
        fp = tempfile.NamedTemporaryFile()
    except ImportError:
        fp = open('/tmp/_osx_support.%s' % (os.getpid(),), 'w+b')

    with contextlib.closing(fp) as fp:
        cmd = "%s 2>/dev/null >'%s'" % (commandstring, fp.name)
        if not os.system(cmd):
            return fp.read().strip()
        return
    return


def _find_build_tool(toolname):
    return _find_executable(toolname) or _read_output('/usr/bin/xcrun -find %s' % (toolname,)) or ''


_SYSTEM_VERSION = None

def _get_system_version():
    global _SYSTEM_VERSION
    if _SYSTEM_VERSION is None:
        _SYSTEM_VERSION = ''
        try:
            f = open('/System/Library/CoreServices/SystemVersion.plist')
        except IOError:
            pass
        else:
            try:
                m = re.search('<key>ProductUserVisibleVersion</key>\\s*<string>(.*?)</string>', f.read())
            finally:
                f.close()

            if m is not None:
                _SYSTEM_VERSION = '.'.join(m.group(1).split('.')[:2])
    return _SYSTEM_VERSION


def _remove_original_values(_config_vars):
    for k in list(_config_vars):
        if k.startswith(_INITPRE):
            del _config_vars[k]


def _save_modified_value(_config_vars, cv, newvalue):
    oldvalue = _config_vars.get(cv, '')
    if oldvalue != newvalue and _INITPRE + cv not in _config_vars:
        _config_vars[_INITPRE + cv] = oldvalue
    _config_vars[cv] = newvalue


def _supports_universal_builds():
    osx_version = _get_system_version()
    if osx_version:
        try:
            osx_version = tuple((int(i) for i in osx_version.split('.')))
        except ValueError:
            osx_version = ''

    return bool(osx_version >= (10, 4)) if osx_version else False


def _find_appropriate_compiler(_config_vars):
    if 'CC' in os.environ:
        return _config_vars
    cc = oldcc = _config_vars['CC'].split()[0]
    if not _find_executable(cc):
        cc = _find_build_tool('clang')
    elif os.path.basename(cc).startswith('gcc'):
        data = _read_output("'%s' --version" % (cc.replace("'", '\'"\'"\''),))
        if data and 'llvm-gcc' in data:
            cc = _find_build_tool('clang')
    if not cc:
        raise SystemError('Cannot locate working compiler')
    if cc != oldcc:
        for cv in _COMPILER_CONFIG_VARS:
            if cv in _config_vars and cv not in os.environ:
                cv_split = _config_vars[cv].split()
                cv_split[0] = cc if cv != 'CXX' else cc + '++'
                _save_modified_value(_config_vars, cv, ' '.join(cv_split))

    return _config_vars


def _remove_universal_flags(_config_vars):
    for cv in _UNIVERSAL_CONFIG_VARS:
        if cv in _config_vars and cv not in os.environ:
            flags = _config_vars[cv]
            flags = re.sub('-arch\\s+\\w+\\s', ' ', flags)
            flags = re.sub('-isysroot [^ \t]*', ' ', flags)
            _save_modified_value(_config_vars, cv, flags)

    return _config_vars


def _remove_unsupported_archs(_config_vars):
    if 'CC' in os.environ:
        return _config_vars
    else:
        if re.search('-arch\\s+ppc', _config_vars['CFLAGS']) is not None:
            status = os.system("echo 'int main{};' | '%s' -c -arch ppc -x c -o /dev/null /dev/null 2>/dev/null" % (_config_vars['CC'].replace("'", '\'"\'"\''),))
            if status:
                for cv in _UNIVERSAL_CONFIG_VARS:
                    if cv in _config_vars and cv not in os.environ:
                        flags = _config_vars[cv]
                        flags = re.sub('-arch\\s+ppc\\w*\\s', ' ', flags)
                        _save_modified_value(_config_vars, cv, flags)

        return _config_vars


def _override_all_archs(_config_vars):
    if 'ARCHFLAGS' in os.environ:
        arch = os.environ['ARCHFLAGS']
        for cv in _UNIVERSAL_CONFIG_VARS:
            if cv in _config_vars and '-arch' in _config_vars[cv]:
                flags = _config_vars[cv]
                flags = re.sub('-arch\\s+\\w+\\s', ' ', flags)
                flags = flags + ' ' + arch
                _save_modified_value(_config_vars, cv, flags)

    return _config_vars


def _check_for_unavailable_sdk(_config_vars):
    cflags = _config_vars.get('CFLAGS', '')
    m = re.search('-isysroot\\s+(\\S+)', cflags)
    if m is not None:
        sdk = m.group(1)
        if not os.path.exists(sdk):
            for cv in _UNIVERSAL_CONFIG_VARS:
                if cv in _config_vars and cv not in os.environ:
                    flags = _config_vars[cv]
                    flags = re.sub('-isysroot\\s+\\S+(?:\\s|$)', ' ', flags)
                    _save_modified_value(_config_vars, cv, flags)

    return _config_vars


def compiler_fixup(compiler_so, cc_args):
    stripArch = stripSysroot = False
    compiler_so = list(compiler_so)
    if not _supports_universal_builds():
        stripArch = stripSysroot = True
    else:
        stripArch = '-arch' in cc_args
        stripSysroot = '-isysroot' in cc_args
    if stripArch or 'ARCHFLAGS' in os.environ:
        while True:
            try:
                index = compiler_so.index('-arch')
                del compiler_so[index:index + 2]
            except ValueError:
                break

    if 'ARCHFLAGS' in os.environ and not stripArch:
        compiler_so = compiler_so + os.environ['ARCHFLAGS'].split()
    if stripSysroot:
        while True:
            try:
                index = compiler_so.index('-isysroot')
                del compiler_so[index:index + 2]
            except ValueError:
                break

    sysroot = None
    if '-isysroot' in cc_args:
        idx = cc_args.index('-isysroot')
        sysroot = cc_args[idx + 1]
    elif '-isysroot' in compiler_so:
        idx = compiler_so.index('-isysroot')
        sysroot = compiler_so[idx + 1]
    if sysroot and not os.path.isdir(sysroot):
        from distutils import log
        log.warn("Compiling with an SDK that doesn't seem to exist: %s", sysroot)
        log.warn('Please check your Xcode installation')
    return compiler_so


def customize_config_vars(_config_vars):
    if not _supports_universal_builds():
        _remove_universal_flags(_config_vars)
    _override_all_archs(_config_vars)
    _check_for_unavailable_sdk(_config_vars)
    return _config_vars


def customize_compiler(_config_vars):
    _find_appropriate_compiler(_config_vars)
    _remove_unsupported_archs(_config_vars)
    _override_all_archs(_config_vars)
    return _config_vars


def get_platform_osx(_config_vars, osname, release, machine):
    macver = _config_vars.get('MACOSX_DEPLOYMENT_TARGET', '')
    macrelease = _get_system_version() or macver
    macver = macver or macrelease
    if macver:
        release = macver
        osname = 'macosx'
        cflags = _config_vars.get(_INITPRE + 'CFLAGS', _config_vars.get('CFLAGS', ''))
        if macrelease:
            try:
                macrelease = tuple((int(i) for i in macrelease.split('.')[0:2]))
            except ValueError:
                macrelease = (10, 0)

        else:
            macrelease = (10, 0)
        if macrelease >= (10, 4) and '-arch' in cflags.strip():
            machine = 'fat'
            archs = re.findall('-arch\\s+(\\S+)', cflags)
            archs = tuple(sorted(set(archs)))
            if len(archs) == 1:
                machine = archs[0]
            elif archs == ('i386', 'ppc'):
                machine = 'fat'
            elif archs == ('i386', 'x86_64'):
                machine = 'intel'
            elif archs == ('i386', 'ppc', 'x86_64'):
                machine = 'fat3'
            elif archs == ('ppc64', 'x86_64'):
                machine = 'fat64'
            elif archs == ('i386', 'ppc', 'ppc64', 'x86_64'):
                machine = 'universal'
            else:
                raise ValueError("Don't know machine value for archs=%r" % (archs,))
        elif machine == 'i386':
            if sys.maxint >= 4294967296L:
                machine = 'x86_64'
        elif machine in ('PowerPC', 'Power_Macintosh'):
            if sys.maxint >= 4294967296L:
                machine = 'ppc64'
            else:
                machine = 'ppc'
    return (osname, release, machine)
