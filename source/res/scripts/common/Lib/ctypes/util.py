# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/util.py
import os
import subprocess
import sys
if os.name == 'nt':

    def _get_build_version():
        prefix = 'MSC v.'
        i = sys.version.find(prefix)
        if i == -1:
            return 6
        else:
            i = i + len(prefix)
            s, rest = sys.version[i:].split(' ', 1)
            majorVersion = int(s[:-2]) - 6
            minorVersion = int(s[2:3]) / 10.0
            if majorVersion == 6:
                minorVersion = 0
            return majorVersion + minorVersion if majorVersion >= 6 else None


    def find_msvcrt():
        version = _get_build_version()
        if version is None:
            return
        else:
            if version <= 6:
                clibname = 'msvcrt'
            else:
                clibname = 'msvcr%d' % (version * 10)
            import imp
            if imp.get_suffixes()[0][0] == '_d.pyd':
                clibname += 'd'
            return clibname + '.dll'


    def find_library(name):
        if name in ('c', 'm'):
            return find_msvcrt()
        else:
            for directory in os.environ['PATH'].split(os.pathsep):
                fname = os.path.join(directory, name)
                if os.path.isfile(fname):
                    return fname
                if fname.lower().endswith('.dll'):
                    continue
                fname = fname + '.dll'
                if os.path.isfile(fname):
                    return fname

            return None


if os.name == 'ce':

    def find_library(name):
        return name


if os.name == 'posix' and sys.platform == 'darwin':
    from ctypes.macholib.dyld import dyld_find as _dyld_find

    def find_library(name):
        possible = ['lib%s.dylib' % name, '%s.dylib' % name, '%s.framework/%s' % (name, name)]
        for name in possible:
            try:
                return _dyld_find(name)
            except ValueError:
                continue

        return None


elif os.name == 'posix':
    import re, tempfile, errno

    def _findLib_gcc(name):
        expr = '[^\\(\\)\\s]*lib%s\\.[^\\(\\)\\s]*' % re.escape(name)
        cmd = 'if type gcc >/dev/null 2>&1; then CC=gcc; elif type cc >/dev/null 2>&1; then CC=cc;else exit; fi;LANG=C LC_ALL=C $CC -Wl,-t -o "$2" 2>&1 -l"$1"'
        temp = tempfile.NamedTemporaryFile()
        try:
            proc = subprocess.Popen((cmd,
             '_findLib_gcc',
             name,
             temp.name), shell=True, stdout=subprocess.PIPE)
            trace, _ = proc.communicate()
        finally:
            try:
                temp.close()
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

        res = re.search(expr, trace)
        return None if not res else res.group(0)


    if sys.platform == 'sunos5':

        def _get_soname(f):
            if not f:
                return
            else:
                null = open(os.devnull, 'wb')
                try:
                    with null:
                        proc = subprocess.Popen(('/usr/ccs/bin/dump', '-Lpv', f), stdout=subprocess.PIPE, stderr=null)
                except OSError:
                    return

                data, _ = proc.communicate()
                res = re.search('\\[.*\\]\\sSONAME\\s+([^\\s]+)', data)
                return None if not res else res.group(1)


    else:

        def _get_soname(f):
            if not f:
                return None
            else:
                cmd = 'if ! type objdump >/dev/null 2>&1; then exit; fi;objdump -p -j .dynamic 2>/dev/null "$1"'
                proc = subprocess.Popen((cmd, '_get_soname', f), shell=True, stdout=subprocess.PIPE)
                dump, _ = proc.communicate()
                res = re.search('\\sSONAME\\s+([^\\s]+)', dump)
                return None if not res else res.group(1)


    if sys.platform.startswith('freebsd') or sys.platform.startswith('openbsd') or sys.platform.startswith('dragonfly'):

        def _num_version(libname):
            parts = libname.split('.')
            nums = []
            try:
                while parts:
                    nums.insert(0, int(parts.pop()))

            except ValueError:
                pass

            return nums or [sys.maxint]


        def find_library(name):
            ename = re.escape(name)
            expr = ':-l%s\\.\\S+ => \\S*/(lib%s\\.\\S+)' % (ename, ename)
            null = open(os.devnull, 'wb')
            try:
                with null:
                    proc = subprocess.Popen(('/sbin/ldconfig', '-r'), stdout=subprocess.PIPE, stderr=null)
            except OSError:
                data = ''
            else:
                data, _ = proc.communicate()

            res = re.findall(expr, data)
            if not res:
                return _get_soname(_findLib_gcc(name))
            res.sort(key=_num_version)
            return res[-1]


    elif sys.platform == 'sunos5':

        def _findLib_crle(name, is64):
            if not os.path.exists('/usr/bin/crle'):
                return
            else:
                env = dict(os.environ)
                env['LC_ALL'] = 'C'
                if is64:
                    args = ('/usr/bin/crle', '-64')
                else:
                    args = ('/usr/bin/crle',)
                paths = None
                null = open(os.devnull, 'wb')
                try:
                    with null:
                        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=null, env=env)
                except OSError:
                    return

                try:
                    for line in proc.stdout:
                        line = line.strip()
                        if line.startswith('Default Library Path (ELF):'):
                            paths = line.split()[4]

                finally:
                    proc.stdout.close()
                    proc.wait()

                if not paths:
                    return
                for dir in paths.split(':'):
                    libfile = os.path.join(dir, 'lib%s.so' % name)
                    if os.path.exists(libfile):
                        return libfile

                return


        def find_library(name, is64=False):
            return _get_soname(_findLib_crle(name, is64) or _findLib_gcc(name))


    else:

        def _findSoname_ldconfig(name):
            import struct
            if struct.calcsize('l') == 4:
                machine = os.uname()[4] + '-32'
            else:
                machine = os.uname()[4] + '-64'
            mach_map = {'x86_64-64': 'libc6,x86-64',
             'ppc64-64': 'libc6,64bit',
             'sparc64-64': 'libc6,64bit',
             's390x-64': 'libc6,64bit',
             'ia64-64': 'libc6,IA-64'}
            abi_type = mach_map.get(machine, 'libc6')
            expr = '\\s+(lib%s\\.[^\\s]+)\\s+\\(%s' % (re.escape(name), abi_type)
            env = dict(os.environ)
            env['LC_ALL'] = 'C'
            env['LANG'] = 'C'
            null = open(os.devnull, 'wb')
            try:
                with null:
                    p = subprocess.Popen(['/sbin/ldconfig', '-p'], stderr=null, stdout=subprocess.PIPE, env=env)
            except OSError:
                return

            data, _ = p.communicate()
            res = re.search(expr, data)
            return None if not res else res.group(1)


        def find_library(name):
            return _findSoname_ldconfig(name) or _get_soname(_findLib_gcc(name))


def test():
    from ctypes import cdll
    if os.name == 'nt':
        print cdll.msvcrt
        print cdll.load('msvcrt')
        print find_library('msvcrt')
    if os.name == 'posix':
        print find_library('m')
        print find_library('c')
        print find_library('bz2')
        if sys.platform == 'darwin':
            print cdll.LoadLibrary('libm.dylib')
            print cdll.LoadLibrary('libcrypto.dylib')
            print cdll.LoadLibrary('libSystem.dylib')
            print cdll.LoadLibrary('System.framework/System')
        else:
            print cdll.LoadLibrary('libm.so')
            print cdll.LoadLibrary('libcrypt.so')
            print find_library('crypt')


if __name__ == '__main__':
    test()
