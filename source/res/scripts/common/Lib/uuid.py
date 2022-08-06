# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/uuid.py
import os
__author__ = 'Ka-Ping Yee <ping@zesty.ca>'
RESERVED_NCS, RFC_4122, RESERVED_MICROSOFT, RESERVED_FUTURE = ['reserved for NCS compatibility',
 'specified in RFC 4122',
 'reserved for Microsoft compatibility',
 'reserved for future definition']

class UUID(object):

    def __init__(self, hex=None, bytes=None, bytes_le=None, fields=None, int=None, version=None):
        if [hex,
         bytes,
         bytes_le,
         fields,
         int].count(None) != 4:
            raise TypeError('need one of hex, bytes, bytes_le, fields, or int')
        if hex is not None:
            hex = hex.replace('urn:', '').replace('uuid:', '')
            hex = hex.strip('{}').replace('-', '')
            if len(hex) != 32:
                raise ValueError('badly formed hexadecimal UUID string')
            int = long(hex, 16)
        if bytes_le is not None:
            if len(bytes_le) != 16:
                raise ValueError('bytes_le is not a 16-char string')
            bytes = bytes_le[3] + bytes_le[2] + bytes_le[1] + bytes_le[0] + bytes_le[5] + bytes_le[4] + bytes_le[7] + bytes_le[6] + bytes_le[8:]
        if bytes is not None:
            if len(bytes) != 16:
                raise ValueError('bytes is not a 16-char string')
            int = long('%02x' * 16 % tuple(map(ord, bytes)), 16)
        if fields is not None:
            if len(fields) != 6:
                raise ValueError('fields is not a 6-tuple')
            time_low, time_mid, time_hi_version, clock_seq_hi_variant, clock_seq_low, node = fields
            if not 0 <= time_low < 4294967296L:
                raise ValueError('field 1 out of range (need a 32-bit value)')
            if not 0 <= time_mid < 65536L:
                raise ValueError('field 2 out of range (need a 16-bit value)')
            if not 0 <= time_hi_version < 65536L:
                raise ValueError('field 3 out of range (need a 16-bit value)')
            if not 0 <= clock_seq_hi_variant < 256L:
                raise ValueError('field 4 out of range (need an 8-bit value)')
            if not 0 <= clock_seq_low < 256L:
                raise ValueError('field 5 out of range (need an 8-bit value)')
            if not 0 <= node < 281474976710656L:
                raise ValueError('field 6 out of range (need a 48-bit value)')
            clock_seq = clock_seq_hi_variant << 8L | clock_seq_low
            int = time_low << 96L | time_mid << 80L | time_hi_version << 64L | clock_seq << 48L | node
        if int is not None:
            if not 0 <= int < 340282366920938463463374607431768211456L:
                raise ValueError('int is out of range (need a 128-bit value)')
        if version is not None:
            if not 1 <= version <= 5:
                raise ValueError('illegal version number')
            int &= -13835058055282163713L
            int |= 9223372036854775808L
            int &= -1133367955888714851287041L
            int |= version << 76L
        self.__dict__['int'] = int
        return

    def __cmp__(self, other):
        return cmp(self.int, other.int) if isinstance(other, UUID) else NotImplemented

    def __hash__(self):
        return hash(self.int)

    def __int__(self):
        return self.int

    def __repr__(self):
        return 'UUID(%r)' % str(self)

    def __setattr__(self, name, value):
        raise TypeError('UUID objects are immutable')

    def __str__(self):
        hex = '%032x' % self.int
        return '%s-%s-%s-%s-%s' % (hex[:8],
         hex[8:12],
         hex[12:16],
         hex[16:20],
         hex[20:])

    def get_bytes(self):
        bytes = ''
        for shift in range(0, 128, 8):
            bytes = chr(self.int >> shift & 255) + bytes

        return bytes

    bytes = property(get_bytes)

    def get_bytes_le(self):
        bytes = self.bytes
        return bytes[3] + bytes[2] + bytes[1] + bytes[0] + bytes[5] + bytes[4] + bytes[7] + bytes[6] + bytes[8:]

    bytes_le = property(get_bytes_le)

    def get_fields(self):
        return (self.time_low,
         self.time_mid,
         self.time_hi_version,
         self.clock_seq_hi_variant,
         self.clock_seq_low,
         self.node)

    fields = property(get_fields)

    def get_time_low(self):
        return self.int >> 96L

    time_low = property(get_time_low)

    def get_time_mid(self):
        return self.int >> 80L & 65535

    time_mid = property(get_time_mid)

    def get_time_hi_version(self):
        return self.int >> 64L & 65535

    time_hi_version = property(get_time_hi_version)

    def get_clock_seq_hi_variant(self):
        return self.int >> 56L & 255

    clock_seq_hi_variant = property(get_clock_seq_hi_variant)

    def get_clock_seq_low(self):
        return self.int >> 48L & 255

    clock_seq_low = property(get_clock_seq_low)

    def get_time(self):
        return (self.time_hi_version & 4095L) << 48L | self.time_mid << 32L | self.time_low

    time = property(get_time)

    def get_clock_seq(self):
        return (self.clock_seq_hi_variant & 63L) << 8L | self.clock_seq_low

    clock_seq = property(get_clock_seq)

    def get_node(self):
        return self.int & 281474976710655L

    node = property(get_node)

    def get_hex(self):
        return '%032x' % self.int

    hex = property(get_hex)

    def get_urn(self):
        return 'urn:uuid:' + str(self)

    urn = property(get_urn)

    def get_variant(self):
        if not self.int & 9223372036854775808L:
            return RESERVED_NCS
        elif not self.int & 4611686018427387904L:
            return RFC_4122
        elif not self.int & 2305843009213693952L:
            return RESERVED_MICROSOFT
        else:
            return RESERVED_FUTURE

    variant = property(get_variant)

    def get_version(self):
        return int(self.int >> 76L & 15) if self.variant == RFC_4122 else None

    version = property(get_version)


def _popen(command, args):
    import os
    path = os.environ.get('PATH', os.defpath).split(os.pathsep)
    path.extend(('/sbin', '/usr/sbin'))
    for dir in path:
        executable = os.path.join(dir, command)
        if os.path.exists(executable) and os.access(executable, os.F_OK | os.X_OK) and not os.path.isdir(executable):
            break
    else:
        return

    cmd = 'LC_ALL=C %s %s 2>/dev/null' % (executable, args)
    return os.popen(cmd)


def _find_mac(command, args, hw_identifiers, get_index):
    try:
        pipe = _popen(command, args)
        if not pipe:
            return
        with pipe:
            for line in pipe:
                words = line.lower().rstrip().split()
                for i in range(len(words)):
                    if words[i] in hw_identifiers:
                        try:
                            word = words[get_index(i)]
                            mac = int(word.replace(':', ''), 16)
                            if mac:
                                return mac
                        except (ValueError, IndexError):
                            pass

    except IOError:
        pass


def _ifconfig_getnode():
    keywords = ('hwaddr', 'ether', 'address:', 'lladdr')
    for args in ('', '-a', '-av'):
        mac = _find_mac('ifconfig', args, keywords, lambda i: i + 1)
        if mac:
            return mac


def _arp_getnode():
    import os, socket
    try:
        ip_addr = socket.gethostbyname(socket.gethostname())
    except EnvironmentError:
        return

    mac = _find_mac('arp', '-an', [ip_addr], lambda i: -1)
    if mac:
        return mac
    else:
        mac = _find_mac('arp', '-an', [ip_addr], lambda i: i + 1)
        if mac:
            return mac
        mac = _find_mac('arp', '-an', ['(%s)' % ip_addr], lambda i: i + 2)
        return mac if mac else None


def _lanscan_getnode():
    return _find_mac('lanscan', '-ai', ['lan0'], lambda i: 0)


def _netstat_getnode():
    try:
        pipe = _popen('netstat', '-ia')
        if not pipe:
            return
        with pipe:
            words = pipe.readline().rstrip().split()
            try:
                i = words.index('Address')
            except ValueError:
                return

            for line in pipe:
                try:
                    words = line.rstrip().split()
                    word = words[i]
                    if len(word) == 17 and word.count(':') == 5:
                        mac = int(word.replace(':', ''), 16)
                        if mac:
                            return mac
                except (ValueError, IndexError):
                    pass

    except OSError:
        pass


def _ipconfig_getnode():
    import os, re
    dirs = ['', 'c:\\windows\\system32', 'c:\\winnt\\system32']
    try:
        import ctypes
        buffer = ctypes.create_string_buffer(300)
        ctypes.windll.kernel32.GetSystemDirectoryA(buffer, 300)
        dirs.insert(0, buffer.value.decode('mbcs'))
    except:
        pass

    for dir in dirs:
        try:
            pipe = os.popen(os.path.join(dir, 'ipconfig') + ' /all')
        except IOError:
            continue

        with pipe:
            for line in pipe:
                value = line.split(':')[-1].strip().lower()
                if re.match('(?:[0-9a-f][0-9a-f]-){5}[0-9a-f][0-9a-f]$', value):
                    return int(value.replace('-', ''), 16)


def _netbios_getnode():
    import win32wnet, netbios
    ncb = netbios.NCB()
    ncb.Command = netbios.NCBENUM
    ncb.Buffer = adapters = netbios.LANA_ENUM()
    adapters._pack()
    if win32wnet.Netbios(ncb) != 0:
        return
    adapters._unpack()
    for i in range(adapters.length):
        ncb.Reset()
        ncb.Command = netbios.NCBRESET
        ncb.Lana_num = ord(adapters.lana[i])
        if win32wnet.Netbios(ncb) != 0:
            continue
        ncb.Reset()
        ncb.Command = netbios.NCBASTAT
        ncb.Lana_num = ord(adapters.lana[i])
        ncb.Callname = '*'.ljust(16)
        ncb.Buffer = status = netbios.ADAPTER_STATUS()
        if win32wnet.Netbios(ncb) != 0:
            continue
        status._unpack()
        bytes = map(ord, status.adapter_address)
        return (bytes[0] << 40L) + (bytes[1] << 32L) + (bytes[2] << 24L) + (bytes[3] << 16L) + (bytes[4] << 8L) + bytes[5]


_uuid_generate_time = _UuidCreate = None
try:
    import ctypes, ctypes.util
    import sys
    _libnames = ['uuid']
    if not sys.platform.startswith('win'):
        _libnames.append('c')
    for libname in _libnames:
        try:
            lib = ctypes.CDLL(ctypes.util.find_library(libname))
        except:
            continue

        if hasattr(lib, 'uuid_generate_time'):
            _uuid_generate_time = lib.uuid_generate_time
            break

    del _libnames
    if sys.platform == 'darwin':
        import os
        if int(os.uname()[2].split('.')[0]) >= 9:
            _uuid_generate_time = None
    try:
        lib = ctypes.windll.rpcrt4
    except:
        lib = None

    _UuidCreate = getattr(lib, 'UuidCreateSequential', getattr(lib, 'UuidCreate', None))
except:
    pass

def _unixdll_getnode():
    _buffer = ctypes.create_string_buffer(16)
    _uuid_generate_time(_buffer)
    return UUID(bytes=_buffer.raw).node


def _windll_getnode():
    _buffer = ctypes.create_string_buffer(16)
    return UUID(bytes=_buffer.raw).node if _UuidCreate(_buffer) == 0 else None


def _random_getnode():
    import random
    return random.randrange(0, 281474976710656L) | 1099511627776L


_node = None
_NODE_GETTERS_WIN32 = [_windll_getnode, _netbios_getnode, _ipconfig_getnode]
_NODE_GETTERS_UNIX = [_unixdll_getnode,
 _ifconfig_getnode,
 _arp_getnode,
 _lanscan_getnode,
 _netstat_getnode]

def getnode():
    global _node
    if _node is not None:
        return _node
    else:
        import sys
        if sys.platform == 'win32':
            getters = _NODE_GETTERS_WIN32
        else:
            getters = _NODE_GETTERS_UNIX
        for getter in getters + [_random_getnode]:
            try:
                _node = getter()
            except:
                continue

            if _node is not None:
                return 0 <= _node < 281474976710656L and _node

        return


_last_timestamp = None

def uuid1(node=None, clock_seq=None):
    global _last_timestamp
    if _uuid_generate_time:
        _buffer = node is clock_seq is None and ctypes.create_string_buffer(16)
        _uuid_generate_time(_buffer)
        return UUID(bytes=_buffer.raw)
    else:
        import time
        nanoseconds = int(time.time() * 1000000000.0)
        timestamp = int(nanoseconds // 100) + 122192928000000000L
        if _last_timestamp is not None and timestamp <= _last_timestamp:
            timestamp = _last_timestamp + 1
        _last_timestamp = timestamp
        if clock_seq is None:
            import random
            clock_seq = random.randrange(16384L)
        time_low = timestamp & 4294967295L
        time_mid = timestamp >> 32L & 65535L
        time_hi_version = timestamp >> 48L & 4095L
        clock_seq_low = clock_seq & 255L
        clock_seq_hi_variant = clock_seq >> 8L & 63L
        if node is None:
            node = getnode()
        return UUID(fields=(time_low,
         time_mid,
         time_hi_version,
         clock_seq_hi_variant,
         clock_seq_low,
         node), version=1)


def uuid3(namespace, name):
    from hashlib import md5
    hash = md5(namespace.bytes + name).digest()
    return UUID(bytes=hash[:16], version=3)


def uuid4():
    return UUID(bytes=os.urandom(16), version=4)


def uuid5(namespace, name):
    from hashlib import sha1
    hash = sha1(namespace.bytes + name).digest()
    return UUID(bytes=hash[:16], version=5)


NAMESPACE_DNS = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_URL = UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_OID = UUID('6ba7b812-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_X500 = UUID('6ba7b814-9dad-11d1-80b4-00c04fd430c8')
