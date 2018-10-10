# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/platform.py
__copyright__ = '\n    Copyright (c) 1999-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com\n    Copyright (c) 2000-2010, eGenix.com Software GmbH; mailto:info@egenix.com\n\n    Permission to use, copy, modify, and distribute this software and its\n    documentation for any purpose and without fee or royalty is hereby granted,\n    provided that the above copyright notice appear in all copies and that\n    both that copyright notice and this permission notice appear in\n    supporting documentation or portions thereof, including modifications,\n    that you make.\n\n    EGENIX.COM SOFTWARE GMBH DISCLAIMS ALL WARRANTIES WITH REGARD TO\n    THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND\n    FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,\n    INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING\n    FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,\n    NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION\n    WITH THE USE OR PERFORMANCE OF THIS SOFTWARE !\n\n'
__version__ = '1.0.7'
import sys, string, os, re
try:
    DEV_NULL = os.devnull
except AttributeError:
    if sys.platform in ('dos', 'win32', 'win16', 'os2'):
        DEV_NULL = 'NUL'
    else:
        DEV_NULL = '/dev/null'

_libc_search = re.compile('(__libc_init)|(GLIBC_([0-9.]+))|(libc(_\\w+)?\\.so(?:\\.(\\d[0-9.]*))?)')

def libc_ver(executable=sys.executable, lib='', version='', chunksize=2048):
    if hasattr(os.path, 'realpath'):
        executable = os.path.realpath(executable)
    f = open(executable, 'rb')
    binary = f.read(chunksize)
    pos = 0
    while 1:
        m = _libc_search.search(binary, pos)
        if not m:
            binary = f.read(chunksize)
            if not binary:
                break
            pos = 0
            continue
        libcinit, glibc, glibcversion, so, threads, soversion = m.groups()
        if libcinit and not lib:
            lib = 'libc'
        elif glibc:
            if lib != 'glibc':
                lib = 'glibc'
                version = glibcversion
            elif glibcversion > version:
                version = glibcversion
        elif so:
            if lib != 'glibc':
                lib = 'libc'
                if soversion and soversion > version:
                    version = soversion
                if threads and version[-len(threads):] != threads:
                    version = version + threads
        pos = m.end()

    f.close()
    return (lib, version)


def _dist_try_harder(distname, version, id):
    if os.path.exists('/var/adm/inst-log/info'):
        info = open('/var/adm/inst-log/info').readlines()
        distname = 'SuSE'
        for line in info:
            tv = string.split(line)
            if len(tv) == 2:
                tag, value = tv
            else:
                continue
            if tag == 'MIN_DIST_VERSION':
                version = string.strip(value)
            if tag == 'DIST_IDENT':
                values = string.split(value, '-')
                id = values[2]

        return (distname, version, id)
    if os.path.exists('/etc/.installed'):
        info = open('/etc/.installed').readlines()
        for line in info:
            pkg = string.split(line, '-')
            if len(pkg) >= 2 and pkg[0] == 'OpenLinux':
                return ('OpenLinux', pkg[1], id)

    if os.path.isdir('/usr/lib/setup'):
        verfiles = os.listdir('/usr/lib/setup')
        for n in range(len(verfiles) - 1, -1, -1):
            if verfiles[n][:14] != 'slack-version-':
                del verfiles[n]

        if verfiles:
            verfiles.sort()
            distname = 'slackware'
            version = verfiles[-1][14:]
            return (distname, version, id)
    return (distname, version, id)


_release_filename = re.compile('(\\w+)[-_](release|version)')
_lsb_release_version = re.compile('(.+) release ([\\d.]+)[^(]*(?:\\((.+)\\))?')
_release_version = re.compile('([^0-9]+)(?: release )?([\\d.]+)[^(]*(?:\\((.+)\\))?')
_supported_dists = ('SuSE', 'debian', 'fedora', 'redhat', 'centos', 'mandrake', 'mandriva', 'rocks', 'slackware', 'yellowdog', 'gentoo', 'UnitedLinux', 'turbolinux')

def _parse_release_file(firstline):
    version = ''
    id = ''
    m = _lsb_release_version.match(firstline)
    if m is not None:
        return tuple(m.groups())
    else:
        m = _release_version.match(firstline)
        if m is not None:
            return tuple(m.groups())
        l = string.split(string.strip(firstline))
        if l:
            version = l[0]
            if len(l) > 1:
                id = l[1]
        return ('', version, id)


def linux_distribution(distname='', version='', id='', supported_dists=_supported_dists, full_distribution_name=1):
    try:
        etc = os.listdir('/etc')
    except os.error:
        return (distname, version, id)

    etc.sort()
    for file in etc:
        m = _release_filename.match(file)
        if m is not None:
            _distname, dummy = m.groups()
            if _distname in supported_dists:
                distname = _distname
                break
    else:
        return _dist_try_harder(distname, version, id)

    f = open('/etc/' + file, 'r')
    firstline = f.readline()
    f.close()
    _distname, _version, _id = _parse_release_file(firstline)
    if _distname and full_distribution_name:
        distname = _distname
    if _version:
        version = _version
    if _id:
        id = _id
    return (distname, version, id)


def dist(distname='', version='', id='', supported_dists=_supported_dists):
    return linux_distribution(distname, version, id, supported_dists=supported_dists, full_distribution_name=0)


class _popen:
    tmpfile = ''
    pipe = None
    bufsize = None
    mode = 'r'

    def __init__(self, cmd, mode='r', bufsize=None):
        if mode != 'r':
            raise ValueError, 'popen()-emulation only supports read mode'
        import tempfile
        self.tmpfile = tmpfile = tempfile.mktemp()
        os.system(cmd + ' > %s' % tmpfile)
        self.pipe = open(tmpfile, 'rb')
        self.bufsize = bufsize
        self.mode = mode

    def read(self):
        return self.pipe.read()

    def readlines(self):
        return self.pipe.readlines() if self.bufsize is not None else None

    def close(self, remove=os.unlink, error=os.error):
        if self.pipe:
            rc = self.pipe.close()
        else:
            rc = 255
        if self.tmpfile:
            try:
                remove(self.tmpfile)
            except error:
                pass

        return rc

    __del__ = close


def popen(cmd, mode='r', bufsize=None):
    popen = None
    if os.environ.get('OS', '') == 'Windows_NT':
        try:
            import win32pipe
        except ImportError:
            pass
        else:
            popen = win32pipe.popen

    if popen is None:
        if hasattr(os, 'popen'):
            popen = os.popen
            if sys.platform == 'win32':
                try:
                    popen('')
                except os.error:
                    popen = _popen

        else:
            popen = _popen
    if bufsize is None:
        return popen(cmd, mode)
    else:
        return popen(cmd, mode, bufsize)
        return


def _norm_version(version, build=''):
    l = string.split(version, '.')
    if build:
        l.append(build)
    try:
        ints = map(int, l)
    except ValueError:
        strings = l
    else:
        strings = map(str, ints)

    version = string.join(strings[:3], '.')
    return version


_ver_output = re.compile('(?:([\\w ]+) ([\\w.]+) .*\\[.* ([\\d.]+)\\])')

def _syscmd_ver(system='', release='', version='', supported_platforms=('win32', 'win16', 'dos', 'os2')):
    if sys.platform not in supported_platforms:
        return (system, release, version)
    else:
        for cmd in ('ver', 'command /c ver', 'cmd /c ver'):
            try:
                pipe = popen(cmd)
                info = pipe.read()
                if pipe.close():
                    raise os.error, 'command failed'
            except os.error as why:
                continue
            except IOError as why:
                continue
            else:
                break

        else:
            return (system, release, version)

        info = string.strip(info)
        m = _ver_output.match(info)
        if m is not None:
            system, release, version = m.groups()
            if release[-1] == '.':
                release = release[:-1]
            if version[-1] == '.':
                version = version[:-1]
            version = _norm_version(version)
        return (system, release, version)


def _win32_getvalue(key, name, default=''):
    try:
        from win32api import RegQueryValueEx
    except ImportError:
        import _winreg
        RegQueryValueEx = _winreg.QueryValueEx

    try:
        return RegQueryValueEx(key, name)
    except:
        return default


def win32_ver(release='', version='', csd='', ptype=''):
    try:
        import win32api
        from win32api import RegQueryValueEx, RegOpenKeyEx, RegCloseKey, GetVersionEx
        from win32con import HKEY_LOCAL_MACHINE, VER_PLATFORM_WIN32_NT, VER_PLATFORM_WIN32_WINDOWS, VER_NT_WORKSTATION
    except ImportError:
        try:
            sys.getwindowsversion
        except AttributeError:
            return (release,
             version,
             csd,
             ptype)

        import _winreg
        GetVersionEx = sys.getwindowsversion
        RegQueryValueEx = _winreg.QueryValueEx
        RegOpenKeyEx = _winreg.OpenKeyEx
        RegCloseKey = _winreg.CloseKey
        HKEY_LOCAL_MACHINE = _winreg.HKEY_LOCAL_MACHINE
        VER_PLATFORM_WIN32_WINDOWS = 1
        VER_PLATFORM_WIN32_NT = 2
        VER_NT_WORKSTATION = 1
        VER_NT_SERVER = 3
        REG_SZ = 1

    winver = GetVersionEx()
    maj, min, buildno, plat, csd = winver
    version = '%i.%i.%i' % (maj, min, buildno & 65535)
    if hasattr(winver, 'service_pack'):
        if winver.service_pack != '':
            csd = 'SP%s' % winver.service_pack_major
    elif csd[:13] == 'Service Pack ':
        csd = 'SP' + csd[13:]
    if plat == VER_PLATFORM_WIN32_WINDOWS:
        regkey = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion'
        if maj == 4:
            if min == 0:
                release = '95'
            elif min == 10:
                release = '98'
            elif min == 90:
                release = 'Me'
            else:
                release = 'postMe'
        elif maj == 5:
            release = '2000'
    elif plat == VER_PLATFORM_WIN32_NT:
        regkey = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'
        if maj <= 4:
            release = 'NT'
        elif maj == 5:
            if min == 0:
                release = '2000'
            elif min == 1:
                release = 'XP'
            elif min == 2:
                release = '2003Server'
            else:
                release = 'post2003'
        elif maj == 6:
            if hasattr(winver, 'product_type'):
                product_type = winver.product_type
            else:
                product_type = VER_NT_WORKSTATION
                try:
                    key = RegOpenKeyEx(HKEY_LOCAL_MACHINE, regkey)
                    name, type = RegQueryValueEx(key, 'ProductName')
                    if type == REG_SZ and name.find('Server') != -1:
                        product_type = VER_NT_SERVER
                except WindowsError:
                    pass

            if min == 0:
                if product_type == VER_NT_WORKSTATION:
                    release = 'Vista'
                else:
                    release = '2008Server'
            elif min == 1:
                if product_type == VER_NT_WORKSTATION:
                    release = '7'
                else:
                    release = '2008ServerR2'
            elif min == 2:
                if product_type == VER_NT_WORKSTATION:
                    release = '8'
                else:
                    release = '2012Server'
            else:
                release = 'post2012Server'
    else:
        if not release:
            release = '%i.%i' % (maj, min)
        return (release,
         version,
         csd,
         ptype)
    try:
        keyCurVer = RegOpenKeyEx(HKEY_LOCAL_MACHINE, regkey)
        RegQueryValueEx(keyCurVer, 'SystemRoot')
    except:
        return (release,
         version,
         csd,
         ptype)

    build = _win32_getvalue(keyCurVer, 'CurrentBuildNumber', ('', 1))[0]
    ptype = _win32_getvalue(keyCurVer, 'CurrentType', (ptype, 1))[0]
    version = _norm_version(version, build)
    RegCloseKey(keyCurVer)
    return (release,
     version,
     csd,
     ptype)


def _mac_ver_lookup(selectors, default=None):
    from gestalt import gestalt
    import MacOS
    l = []
    append = l.append
    for selector in selectors:
        try:
            append(gestalt(selector))
        except (RuntimeError, MacOS.Error):
            append(default)

    return l


def _bcd2str(bcd):
    return hex(bcd)[2:]


def _mac_ver_gestalt():
    try:
        import gestalt
        import MacOS
    except ImportError:
        return

    sysv, sysa = _mac_ver_lookup(('sysv', 'sysa'))
    if sysv:
        major = (sysv & 65280) >> 8
        minor = (sysv & 240) >> 4
        patch = sysv & 15
        if (major, minor) >= (10, 4):
            major, minor, patch = _mac_ver_lookup(('sys1', 'sys2', 'sys3'))
            release = '%i.%i.%i' % (major, minor, patch)
        else:
            release = '%s.%i.%i' % (_bcd2str(major), minor, patch)
    if sysa:
        machine = {1: '68k',
         2: 'PowerPC',
         10: 'i386'}.get(sysa, '')
    versioninfo = ('', '', '')
    return (release, versioninfo, machine)


def _mac_ver_xml():
    fn = '/System/Library/CoreServices/SystemVersion.plist'
    if not os.path.exists(fn):
        return
    else:
        try:
            import plistlib
        except ImportError:
            return

        pl = plistlib.readPlist(fn)
        release = pl['ProductVersion']
        versioninfo = ('', '', '')
        machine = os.uname()[4]
        if machine in ('ppc', 'Power Macintosh'):
            machine = 'PowerPC'
        return (release, versioninfo, machine)


def mac_ver(release='', versioninfo=('', '', ''), machine=''):
    info = _mac_ver_xml()
    if info is not None:
        return info
    else:
        info = _mac_ver_gestalt()
        return info if info is not None else (release, versioninfo, machine)


def _java_getprop(name, default):
    from java.lang import System
    try:
        value = System.getProperty(name)
        if value is None:
            return default
        return value
    except AttributeError:
        return default

    return


def java_ver(release='', vendor='', vminfo=('', '', ''), osinfo=('', '', '')):
    try:
        import java.lang
    except ImportError:
        return (release,
         vendor,
         vminfo,
         osinfo)

    vendor = _java_getprop('java.vendor', vendor)
    release = _java_getprop('java.version', release)
    vm_name, vm_release, vm_vendor = vminfo
    vm_name = _java_getprop('java.vm.name', vm_name)
    vm_vendor = _java_getprop('java.vm.vendor', vm_vendor)
    vm_release = _java_getprop('java.vm.version', vm_release)
    vminfo = (vm_name, vm_release, vm_vendor)
    os_name, os_version, os_arch = osinfo
    os_arch = _java_getprop('java.os.arch', os_arch)
    os_name = _java_getprop('java.os.name', os_name)
    os_version = _java_getprop('java.os.version', os_version)
    osinfo = (os_name, os_version, os_arch)
    return (release,
     vendor,
     vminfo,
     osinfo)


def system_alias(system, release, version):
    if system == 'Rhapsody':
        return ('MacOS X Server', system + release, version)
    if system == 'SunOS':
        if release < '5':
            return (system, release, version)
        l = string.split(release, '.')
        if l:
            try:
                major = int(l[0])
            except ValueError:
                pass
            else:
                major = major - 3
                l[0] = str(major)
                release = string.join(l, '.')

        if release < '6':
            system = 'Solaris'
        else:
            system = 'Solaris'
    elif system == 'IRIX64':
        system = 'IRIX'
        if version:
            version = version + ' (64bit)'
        else:
            version = '64bit'
    elif system in ('win32', 'win16'):
        system = 'Windows'
    return (system, release, version)


def _platform(*args):
    platform = string.join(map(string.strip, filter(len, args)), '-')
    replace = string.replace
    platform = replace(platform, ' ', '_')
    platform = replace(platform, '/', '-')
    platform = replace(platform, '\\', '-')
    platform = replace(platform, ':', '-')
    platform = replace(platform, ';', '-')
    platform = replace(platform, '"', '-')
    platform = replace(platform, '(', '-')
    platform = replace(platform, ')', '-')
    platform = replace(platform, 'unknown', '')
    while 1:
        cleaned = replace(platform, '--', '-')
        if cleaned == platform:
            break
        platform = cleaned

    while platform[-1] == '-':
        platform = platform[:-1]

    return platform


def _node(default=''):
    try:
        import socket
    except ImportError:
        return default

    try:
        return socket.gethostname()
    except socket.error:
        return default


if not hasattr(os.path, 'abspath'):

    def _abspath(path, isabs=os.path.isabs, join=os.path.join, getcwd=os.getcwd, normpath=os.path.normpath):
        if not isabs(path):
            path = join(getcwd(), path)
        return normpath(path)


else:
    _abspath = os.path.abspath

def _follow_symlinks(filepath):
    filepath = _abspath(filepath)
    while os.path.islink(filepath):
        filepath = os.path.normpath(os.path.join(os.path.dirname(filepath), os.readlink(filepath)))

    return filepath


def _syscmd_uname(option, default=''):
    if sys.platform in ('dos', 'win32', 'win16', 'os2'):
        return default
    try:
        f = os.popen('uname %s 2> %s' % (option, DEV_NULL))
    except (AttributeError, os.error):
        return default

    output = string.strip(f.read())
    rc = f.close()
    if not output or rc:
        return default
    else:
        return output


def _syscmd_file(target, default=''):
    import subprocess
    if sys.platform in ('dos', 'win32', 'win16', 'os2'):
        return default
    target = _follow_symlinks(target)
    try:
        proc = subprocess.Popen(['file', target], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except (AttributeError, os.error):
        return default

    output = proc.communicate()[0]
    rc = proc.wait()
    if not output or rc:
        return default
    else:
        return output


_default_architecture = {'win32': ('', 'WindowsPE'),
 'win16': ('', 'Windows'),
 'dos': ('', 'MSDOS')}
_architecture_split = re.compile('[\\s,]').split

def architecture(executable=sys.executable, bits='', linkage=''):
    if not bits:
        import struct
        try:
            size = struct.calcsize('P')
        except struct.error:
            size = struct.calcsize('l')

        bits = str(size * 8) + 'bit'
    if executable:
        output = _syscmd_file(executable, '')
    else:
        output = ''
    if not output and executable == sys.executable:
        if sys.platform in _default_architecture:
            b, l = _default_architecture[sys.platform]
            if b:
                bits = b
            if l:
                linkage = l
        return (bits, linkage)
    fileout = _architecture_split(output)[1:]
    if 'executable' not in fileout:
        return (bits, linkage)
    if '32-bit' in fileout:
        bits = '32bit'
    elif 'N32' in fileout:
        bits = 'n32bit'
    elif '64-bit' in fileout:
        bits = '64bit'
    if 'ELF' in fileout:
        linkage = 'ELF'
    elif 'PE' in fileout:
        if 'Windows' in fileout:
            linkage = 'WindowsPE'
        else:
            linkage = 'PE'
    elif 'COFF' in fileout:
        linkage = 'COFF'
    elif 'MS-DOS' in fileout:
        linkage = 'MSDOS'
    return (bits, linkage)


_uname_cache = None

def uname():
    global _uname_cache
    no_os_uname = 0
    if _uname_cache is not None:
        return _uname_cache
    else:
        processor = ''
        try:
            system, node, release, version, machine = os.uname()
        except AttributeError:
            no_os_uname = 1

        if no_os_uname or not filter(None, (system,
         node,
         release,
         version,
         machine)):
            if no_os_uname:
                system = sys.platform
                release = ''
                version = ''
                node = _node()
                machine = ''
            use_syscmd_ver = 1
            if system == 'win32':
                release, version, csd, ptype = win32_ver()
                if release and version:
                    use_syscmd_ver = 0
                if not machine:
                    if 'PROCESSOR_ARCHITEW6432' in os.environ:
                        machine = os.environ.get('PROCESSOR_ARCHITEW6432', '')
                    else:
                        machine = os.environ.get('PROCESSOR_ARCHITECTURE', '')
                if not processor:
                    processor = os.environ.get('PROCESSOR_IDENTIFIER', machine)
            if use_syscmd_ver:
                system, release, version = _syscmd_ver(system)
                if system == 'Microsoft Windows':
                    system = 'Windows'
                elif system == 'Microsoft' and release == 'Windows':
                    system = 'Windows'
                    if '6.0' == version[:3]:
                        release = 'Vista'
                    else:
                        release = ''
            if system in ('win32', 'win16'):
                if not version:
                    if system == 'win32':
                        version = '32bit'
                    else:
                        version = '16bit'
                system = 'Windows'
            elif system[:4] == 'java':
                release, vendor, vminfo, osinfo = java_ver()
                system = 'Java'
                version = string.join(vminfo, ', ')
                if not version:
                    version = vendor
        if system == 'OpenVMS':
            if not release or release == '0':
                release = version
                version = ''
            try:
                import vms_lib
            except ImportError:
                pass
            else:
                csid, cpu_number = vms_lib.getsyi('SYI$_CPU', 0)
                if cpu_number >= 128:
                    processor = 'Alpha'
                else:
                    processor = 'VAX'
        if not processor:
            processor = _syscmd_uname('-p', '')
        if system == 'unknown':
            system = ''
        if node == 'unknown':
            node = ''
        if release == 'unknown':
            release = ''
        if version == 'unknown':
            version = ''
        if machine == 'unknown':
            machine = ''
        if processor == 'unknown':
            processor = ''
        if system == 'Microsoft' and release == 'Windows':
            system = 'Windows'
            release = 'Vista'
        _uname_cache = (system,
         node,
         release,
         version,
         machine,
         processor)
        return _uname_cache


def system():
    return uname()[0]


def node():
    return uname()[1]


def release():
    return uname()[2]


def version():
    return uname()[3]


def machine():
    return uname()[4]


def processor():
    return uname()[5]


_sys_version_parser = re.compile('([\\w.+]+)\\s*\\(#?([^,]+),\\s*([\\w ]+),\\s*([\\w :]+)\\)\\s*\\[([^\\]]+)\\]?')
_ironpython_sys_version_parser = re.compile('IronPython\\s*([\\d\\.]+)(?: \\(([\\d\\.]+)\\))? on (.NET [\\d\\.]+)')
_ironpython26_sys_version_parser = re.compile('([\\d.]+)\\s*\\(IronPython\\s*[\\d.]+\\s*\\(([\\d.]+)\\) on ([\\w.]+ [\\d.]+(?: \\(\\d+-bit\\))?)\\)')
_pypy_sys_version_parser = re.compile('([\\w.+]+)\\s*\\(#?([^,]+),\\s*([\\w ]+),\\s*([\\w :]+)\\)\\s*\\[PyPy [^\\]]+\\]?')
_sys_version_cache = {}

def _sys_version(sys_version=None):
    if sys_version is None:
        sys_version = sys.version
    result = _sys_version_cache.get(sys_version, None)
    if result is not None:
        return result
    else:
        if 'IronPython' in sys_version:
            name = 'IronPython'
            if sys_version.startswith('IronPython'):
                match = _ironpython_sys_version_parser.match(sys_version)
            else:
                match = _ironpython26_sys_version_parser.match(sys_version)
            if match is None:
                raise ValueError('failed to parse IronPython sys.version: %s' % repr(sys_version))
            version, alt_version, compiler = match.groups()
            buildno = ''
            builddate = ''
        elif sys.platform.startswith('java'):
            name = 'Jython'
            match = _sys_version_parser.match(sys_version)
            if match is None:
                raise ValueError('failed to parse Jython sys.version: %s' % repr(sys_version))
            version, buildno, builddate, buildtime, _ = match.groups()
            compiler = sys.platform
        elif 'PyPy' in sys_version:
            name = 'PyPy'
            match = _pypy_sys_version_parser.match(sys_version)
            if match is None:
                raise ValueError('failed to parse PyPy sys.version: %s' % repr(sys_version))
            version, buildno, builddate, buildtime = match.groups()
            compiler = ''
        else:
            match = _sys_version_parser.match(sys_version)
            if match is None:
                raise ValueError('failed to parse CPython sys.version: %s' % repr(sys_version))
            version, buildno, builddate, buildtime, compiler = match.groups()
            name = 'CPython'
            builddate = builddate + ' ' + buildtime
        if hasattr(sys, 'subversion'):
            _, branch, revision = sys.subversion
        else:
            branch = ''
            revision = ''
        l = string.split(version, '.')
        if len(l) == 2:
            l.append('0')
            version = string.join(l, '.')
        result = (name,
         version,
         branch,
         revision,
         buildno,
         builddate,
         compiler)
        _sys_version_cache[sys_version] = result
        return result


def python_implementation():
    return _sys_version()[0]


def python_version():
    return _sys_version()[1]


def python_version_tuple():
    return tuple(string.split(_sys_version()[1], '.'))


def python_branch():
    return _sys_version()[2]


def python_revision():
    return _sys_version()[3]


def python_build():
    return _sys_version()[4:6]


def python_compiler():
    return _sys_version()[6]


_platform_cache = {}

def platform(aliased=0, terse=0):
    result = _platform_cache.get((aliased, terse), None)
    if result is not None:
        return result
    else:
        system, node, release, version, machine, processor = uname()
        if machine == processor:
            processor = ''
        if aliased:
            system, release, version = system_alias(system, release, version)
        if system == 'Windows':
            rel, vers, csd, ptype = win32_ver(version)
            if terse:
                platform = _platform(system, release)
            else:
                platform = _platform(system, release, version, csd)
        elif system in ('Linux',):
            distname, distversion, distid = dist('')
            if distname and not terse:
                platform = _platform(system, release, machine, processor, 'with', distname, distversion, distid)
            else:
                libcname, libcversion = libc_ver(sys.executable)
                platform = _platform(system, release, machine, processor, 'with', libcname + libcversion)
        elif system == 'Java':
            r, v, vminfo, (os_name, os_version, os_arch) = java_ver()
            if terse or not os_name:
                platform = _platform(system, release, version)
            else:
                platform = _platform(system, release, version, 'on', os_name, os_version, os_arch)
        elif system == 'MacOS':
            if terse:
                platform = _platform(system, release)
            else:
                platform = _platform(system, release, machine)
        elif terse:
            platform = _platform(system, release)
        else:
            bits, linkage = architecture(sys.executable)
            platform = _platform(system, release, machine, processor, bits, linkage)
        _platform_cache[aliased, terse] = platform
        return platform


if __name__ == '__main__':
    terse = 'terse' in sys.argv or '--terse' in sys.argv
    aliased = 'nonaliased' not in sys.argv and '--nonaliased' not in sys.argv
    print platform(aliased, terse)
    sys.exit(0)
