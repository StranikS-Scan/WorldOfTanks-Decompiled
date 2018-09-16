# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ftplib.py
import os
import sys
try:
    import SOCKS
    socket = SOCKS
    del SOCKS
    from socket import getfqdn
    socket.getfqdn = getfqdn
    del getfqdn
except ImportError:
    import socket

from socket import _GLOBAL_DEFAULT_TIMEOUT
__all__ = ['FTP', 'Netrc']
MSG_OOB = 1
FTP_PORT = 21
MAXLINE = 8192

class Error(Exception):
    pass


class error_reply(Error):
    pass


class error_temp(Error):
    pass


class error_perm(Error):
    pass


class error_proto(Error):
    pass


all_errors = (Error, IOError, EOFError)
CRLF = '\r\n'

class FTP():
    debugging = 0
    host = ''
    port = FTP_PORT
    maxline = MAXLINE
    sock = None
    file = None
    welcome = None
    passiveserver = 1

    def __init__(self, host='', user='', passwd='', acct='', timeout=_GLOBAL_DEFAULT_TIMEOUT):
        self.timeout = timeout
        if host:
            self.connect(host)
            if user:
                self.login(user, passwd, acct)

    def connect(self, host='', port=0, timeout=-999):
        if host != '':
            self.host = host
        if port > 0:
            self.port = port
        if timeout != -999:
            self.timeout = timeout
        self.sock = socket.create_connection((self.host, self.port), self.timeout)
        self.af = self.sock.family
        self.file = self.sock.makefile('rb')
        self.welcome = self.getresp()
        return self.welcome

    def getwelcome(self):
        if self.debugging:
            print '*welcome*', self.sanitize(self.welcome)
        return self.welcome

    def set_debuglevel(self, level):
        self.debugging = level

    debug = set_debuglevel

    def set_pasv(self, val):
        self.passiveserver = val

    def sanitize(self, s):
        if s[:5] == 'pass ' or s[:5] == 'PASS ':
            i = len(s)
            while i > 5 and s[i - 1] in '\r\n':
                i = i - 1

            s = s[:5] + '*' * (i - 5) + s[i:]
        return repr(s)

    def putline(self, line):
        line = line + CRLF
        if self.debugging > 1:
            print '*put*', self.sanitize(line)
        self.sock.sendall(line)

    def putcmd(self, line):
        if self.debugging:
            print '*cmd*', self.sanitize(line)
        self.putline(line)

    def getline(self):
        line = self.file.readline(self.maxline + 1)
        if len(line) > self.maxline:
            raise Error('got more than %d bytes' % self.maxline)
        if self.debugging > 1:
            print '*get*', self.sanitize(line)
        if not line:
            raise EOFError
        if line[-2:] == CRLF:
            line = line[:-2]
        elif line[-1:] in CRLF:
            line = line[:-1]
        return line

    def getmultiline(self):
        line = self.getline()
        if line[3:4] == '-':
            code = line[:3]
            while 1:
                nextline = self.getline()
                line = line + ('\n' + nextline)
                if nextline[:3] == code and nextline[3:4] != '-':
                    break

        return line

    def getresp(self):
        resp = self.getmultiline()
        if self.debugging:
            print '*resp*', self.sanitize(resp)
        self.lastresp = resp[:3]
        c = resp[:1]
        if c in ('1', '2', '3'):
            return resp
        if c == '4':
            raise error_temp, resp
        if c == '5':
            raise error_perm, resp
        raise error_proto, resp

    def voidresp(self):
        resp = self.getresp()
        if resp[:1] != '2':
            raise error_reply, resp
        return resp

    def abort(self):
        line = 'ABOR' + CRLF
        if self.debugging > 1:
            print '*put urgent*', self.sanitize(line)
        self.sock.sendall(line, MSG_OOB)
        resp = self.getmultiline()
        if resp[:3] not in ('426', '225', '226'):
            raise error_proto, resp

    def sendcmd(self, cmd):
        self.putcmd(cmd)
        return self.getresp()

    def voidcmd(self, cmd):
        self.putcmd(cmd)
        return self.voidresp()

    def sendport(self, host, port):
        hbytes = host.split('.')
        pbytes = [repr(port // 256), repr(port % 256)]
        bytes = hbytes + pbytes
        cmd = 'PORT ' + ','.join(bytes)
        return self.voidcmd(cmd)

    def sendeprt(self, host, port):
        af = 0
        if self.af == socket.AF_INET:
            af = 1
        if self.af == socket.AF_INET6:
            af = 2
        if af == 0:
            raise error_proto, 'unsupported address family'
        fields = ['',
         repr(af),
         host,
         repr(port),
         '']
        cmd = 'EPRT ' + '|'.join(fields)
        return self.voidcmd(cmd)

    def makeport(self):
        err = None
        sock = None
        for res in socket.getaddrinfo(None, 0, self.af, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = res
            try:
                sock = socket.socket(af, socktype, proto)
                sock.bind(sa)
            except socket.error as err:
                if sock:
                    sock.close()
                sock = None
                continue

            break

        if sock is None:
            if err is not None:
                raise err
            else:
                raise socket.error('getaddrinfo returns an empty list')
        sock.listen(1)
        port = sock.getsockname()[1]
        host = self.sock.getsockname()[0]
        if self.af == socket.AF_INET:
            resp = self.sendport(host, port)
        else:
            resp = self.sendeprt(host, port)
        if self.timeout is not _GLOBAL_DEFAULT_TIMEOUT:
            sock.settimeout(self.timeout)
        return sock

    def makepasv(self):
        if self.af == socket.AF_INET:
            host, port = parse227(self.sendcmd('PASV'))
        else:
            host, port = parse229(self.sendcmd('EPSV'), self.sock.getpeername())
        return (host, port)

    def ntransfercmd(self, cmd, rest=None):
        size = None
        if self.passiveserver:
            host, port = self.makepasv()
            conn = socket.create_connection((host, port), self.timeout)
            try:
                if rest is not None:
                    self.sendcmd('REST %s' % rest)
                resp = self.sendcmd(cmd)
                if resp[0] == '2':
                    resp = self.getresp()
                if resp[0] != '1':
                    raise error_reply, resp
            except:
                conn.close()
                raise

        else:
            sock = self.makeport()
            try:
                if rest is not None:
                    self.sendcmd('REST %s' % rest)
                resp = self.sendcmd(cmd)
                if resp[0] == '2':
                    resp = self.getresp()
                if resp[0] != '1':
                    raise error_reply, resp
                conn, sockaddr = sock.accept()
                if self.timeout is not _GLOBAL_DEFAULT_TIMEOUT:
                    conn.settimeout(self.timeout)
            finally:
                sock.close()

        if resp[:3] == '150':
            size = parse150(resp)
        return (conn, size)

    def transfercmd(self, cmd, rest=None):
        return self.ntransfercmd(cmd, rest)[0]

    def login(self, user='', passwd='', acct=''):
        if not user:
            user = 'anonymous'
        if not passwd:
            passwd = ''
        if not acct:
            acct = ''
        if user == 'anonymous' and passwd in ('', '-'):
            passwd = passwd + 'anonymous@'
        resp = self.sendcmd('USER ' + user)
        if resp[0] == '3':
            resp = self.sendcmd('PASS ' + passwd)
        if resp[0] == '3':
            resp = self.sendcmd('ACCT ' + acct)
        if resp[0] != '2':
            raise error_reply, resp
        return resp

    def retrbinary(self, cmd, callback, blocksize=8192, rest=None):
        self.voidcmd('TYPE I')
        conn = self.transfercmd(cmd, rest)
        while 1:
            data = conn.recv(blocksize)
            if not data:
                break
            callback(data)

        conn.close()
        return self.voidresp()

    def retrlines(self, cmd, callback=None):
        if callback is None:
            callback = print_line
        resp = self.sendcmd('TYPE A')
        conn = self.transfercmd(cmd)
        fp = conn.makefile('rb')
        while 1:
            line = fp.readline(self.maxline + 1)
            if len(line) > self.maxline:
                raise Error('got more than %d bytes' % self.maxline)
            if self.debugging > 2:
                print '*retr*', repr(line)
            if not line:
                break
            if line[-2:] == CRLF:
                line = line[:-2]
            elif line[-1:] == '\n':
                line = line[:-1]
            callback(line)

        fp.close()
        conn.close()
        return self.voidresp()

    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        self.voidcmd('TYPE I')
        conn = self.transfercmd(cmd, rest)
        while 1:
            buf = fp.read(blocksize)
            if not buf:
                break
            conn.sendall(buf)
            if callback:
                callback(buf)

        conn.close()
        return self.voidresp()

    def storlines(self, cmd, fp, callback=None):
        self.voidcmd('TYPE A')
        conn = self.transfercmd(cmd)
        while 1:
            buf = fp.readline(self.maxline + 1)
            if len(buf) > self.maxline:
                raise Error('got more than %d bytes' % self.maxline)
            if not buf:
                break
            if buf[-2:] != CRLF:
                if buf[-1] in CRLF:
                    buf = buf[:-1]
                buf = buf + CRLF
            conn.sendall(buf)
            if callback:
                callback(buf)

        conn.close()
        return self.voidresp()

    def acct(self, password):
        cmd = 'ACCT ' + password
        return self.voidcmd(cmd)

    def nlst(self, *args):
        cmd = 'NLST'
        for arg in args:
            cmd = cmd + (' ' + arg)

        files = []
        self.retrlines(cmd, files.append)
        return files

    def dir(self, *args):
        cmd = 'LIST'
        func = None
        if args[-1:] and type(args[-1]) != type(''):
            args, func = args[:-1], args[-1]
        for arg in args:
            if arg:
                cmd = cmd + (' ' + arg)

        self.retrlines(cmd, func)
        return

    def rename(self, fromname, toname):
        resp = self.sendcmd('RNFR ' + fromname)
        if resp[0] != '3':
            raise error_reply, resp
        return self.voidcmd('RNTO ' + toname)

    def delete(self, filename):
        resp = self.sendcmd('DELE ' + filename)
        if resp[:3] in ('250', '200'):
            return resp
        raise error_reply, resp

    def cwd(self, dirname):
        if dirname == '..':
            try:
                return self.voidcmd('CDUP')
            except error_perm as msg:
                if msg.args[0][:3] != '500':
                    raise

        elif dirname == '':
            dirname = '.'
        cmd = 'CWD ' + dirname
        return self.voidcmd(cmd)

    def size(self, filename):
        resp = self.sendcmd('SIZE ' + filename)
        if resp[:3] == '213':
            s = resp[3:].strip()
            try:
                return int(s)
            except (OverflowError, ValueError):
                return long(s)

    def mkd(self, dirname):
        resp = self.sendcmd('MKD ' + dirname)
        return parse257(resp)

    def rmd(self, dirname):
        return self.voidcmd('RMD ' + dirname)

    def pwd(self):
        resp = self.sendcmd('PWD')
        return parse257(resp)

    def quit(self):
        resp = self.voidcmd('QUIT')
        self.close()
        return resp

    def close(self):
        if self.file is not None:
            self.file.close()
        if self.sock is not None:
            self.sock.close()
        self.file = self.sock = None
        return


try:
    import ssl
except ImportError:
    pass
else:

    class FTP_TLS(FTP):
        ssl_version = ssl.PROTOCOL_TLSv1

        def __init__(self, host='', user='', passwd='', acct='', keyfile=None, certfile=None, timeout=_GLOBAL_DEFAULT_TIMEOUT):
            self.keyfile = keyfile
            self.certfile = certfile
            self._prot_p = False
            FTP.__init__(self, host, user, passwd, acct, timeout)

        def login(self, user='', passwd='', acct='', secure=True):
            if secure and not isinstance(self.sock, ssl.SSLSocket):
                self.auth()
            return FTP.login(self, user, passwd, acct)

        def auth(self):
            if isinstance(self.sock, ssl.SSLSocket):
                raise ValueError('Already using TLS')
            if self.ssl_version == ssl.PROTOCOL_TLSv1:
                resp = self.voidcmd('AUTH TLS')
            else:
                resp = self.voidcmd('AUTH SSL')
            self.sock = ssl.wrap_socket(self.sock, self.keyfile, self.certfile, ssl_version=self.ssl_version)
            self.file = self.sock.makefile(mode='rb')
            return resp

        def prot_p(self):
            self.voidcmd('PBSZ 0')
            resp = self.voidcmd('PROT P')
            self._prot_p = True
            return resp

        def prot_c(self):
            resp = self.voidcmd('PROT C')
            self._prot_p = False
            return resp

        def ntransfercmd(self, cmd, rest=None):
            conn, size = FTP.ntransfercmd(self, cmd, rest)
            if self._prot_p:
                conn = ssl.wrap_socket(conn, self.keyfile, self.certfile, ssl_version=self.ssl_version)
            return (conn, size)

        def retrbinary(self, cmd, callback, blocksize=8192, rest=None):
            self.voidcmd('TYPE I')
            conn = self.transfercmd(cmd, rest)
            try:
                while 1:
                    data = conn.recv(blocksize)
                    if not data:
                        break
                    callback(data)

                if isinstance(conn, ssl.SSLSocket):
                    conn.unwrap()
            finally:
                conn.close()

            return self.voidresp()

        def retrlines(self, cmd, callback=None):
            if callback is None:
                callback = print_line
            resp = self.sendcmd('TYPE A')
            conn = self.transfercmd(cmd)
            fp = conn.makefile('rb')
            try:
                while 1:
                    line = fp.readline(self.maxline + 1)
                    if len(line) > self.maxline:
                        raise Error('got more than %d bytes' % self.maxline)
                    if self.debugging > 2:
                        print '*retr*', repr(line)
                    if not line:
                        break
                    if line[-2:] == CRLF:
                        line = line[:-2]
                    elif line[-1:] == '\n':
                        line = line[:-1]
                    callback(line)

                if isinstance(conn, ssl.SSLSocket):
                    conn.unwrap()
            finally:
                fp.close()
                conn.close()

            return self.voidresp()

        def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
            self.voidcmd('TYPE I')
            conn = self.transfercmd(cmd, rest)
            try:
                while 1:
                    buf = fp.read(blocksize)
                    if not buf:
                        break
                    conn.sendall(buf)
                    if callback:
                        callback(buf)

                if isinstance(conn, ssl.SSLSocket):
                    conn.unwrap()
            finally:
                conn.close()

            return self.voidresp()

        def storlines(self, cmd, fp, callback=None):
            self.voidcmd('TYPE A')
            conn = self.transfercmd(cmd)
            try:
                while 1:
                    buf = fp.readline(self.maxline + 1)
                    if len(buf) > self.maxline:
                        raise Error('got more than %d bytes' % self.maxline)
                    if not buf:
                        break
                    if buf[-2:] != CRLF:
                        if buf[-1] in CRLF:
                            buf = buf[:-1]
                        buf = buf + CRLF
                    conn.sendall(buf)
                    if callback:
                        callback(buf)

                if isinstance(conn, ssl.SSLSocket):
                    conn.unwrap()
            finally:
                conn.close()

            return self.voidresp()


    __all__.append('FTP_TLS')
    all_errors = (Error,
     IOError,
     EOFError,
     ssl.SSLError)

_150_re = None

def parse150(resp):
    global _150_re
    if resp[:3] != '150':
        raise error_reply, resp
    if _150_re is None:
        import re
        _150_re = re.compile('150 .* \\((\\d+) bytes\\)', re.IGNORECASE)
    m = _150_re.match(resp)
    if not m:
        return
    else:
        s = m.group(1)
        try:
            return int(s)
        except (OverflowError, ValueError):
            return long(s)

        return


_227_re = None

def parse227(resp):
    global _227_re
    if resp[:3] != '227':
        raise error_reply, resp
    if _227_re is None:
        import re
        _227_re = re.compile('(\\d+),(\\d+),(\\d+),(\\d+),(\\d+),(\\d+)')
    m = _227_re.search(resp)
    if not m:
        raise error_proto, resp
    numbers = m.groups()
    host = '.'.join(numbers[:4])
    port = (int(numbers[4]) << 8) + int(numbers[5])
    return (host, port)


def parse229(resp, peer):
    if resp[:3] != '229':
        raise error_reply, resp
    left = resp.find('(')
    if left < 0:
        raise error_proto, resp
    right = resp.find(')', left + 1)
    if right < 0:
        raise error_proto, resp
    if resp[left + 1] != resp[right - 1]:
        raise error_proto, resp
    parts = resp[left + 1:right].split(resp[left + 1])
    if len(parts) != 5:
        raise error_proto, resp
    host = peer[0]
    port = int(parts[3])
    return (host, port)


def parse257(resp):
    if resp[:3] != '257':
        raise error_reply, resp
    if resp[3:5] != ' "':
        return ''
    dirname = ''
    i = 5
    n = len(resp)
    while i < n:
        c = resp[i]
        i = i + 1
        if c == '"':
            if i >= n or resp[i] != '"':
                break
            i = i + 1
        dirname = dirname + c

    return dirname


def print_line(line):
    print line


def ftpcp(source, sourcename, target, targetname='', type='I'):
    if not targetname:
        targetname = sourcename
    type = 'TYPE ' + type
    source.voidcmd(type)
    target.voidcmd(type)
    sourcehost, sourceport = parse227(source.sendcmd('PASV'))
    target.sendport(sourcehost, sourceport)
    treply = target.sendcmd('STOR ' + targetname)
    if treply[:3] not in ('125', '150'):
        raise error_proto
    sreply = source.sendcmd('RETR ' + sourcename)
    if sreply[:3] not in ('125', '150'):
        raise error_proto
    source.voidresp()
    target.voidresp()


class Netrc():
    __defuser = None
    __defpasswd = None
    __defacct = None

    def __init__(self, filename=None):
        if filename is None:
            if 'HOME' in os.environ:
                filename = os.path.join(os.environ['HOME'], '.netrc')
            else:
                raise IOError, 'specify file to load or set $HOME'
        self.__hosts = {}
        self.__macros = {}
        fp = open(filename, 'r')
        in_macro = 0
        while 1:
            line = fp.readline(self.maxline + 1)
            if len(line) > self.maxline:
                raise Error('got more than %d bytes' % self.maxline)
            if not line:
                break
            if in_macro and line.strip():
                macro_lines.append(line)
                continue
            elif in_macro:
                self.__macros[macro_name] = tuple(macro_lines)
                in_macro = 0
            words = line.split()
            host = user = passwd = acct = None
            default = 0
            i = 0
            while i < len(words):
                w1 = words[i]
                if i + 1 < len(words):
                    w2 = words[i + 1]
                else:
                    w2 = None
                if w1 == 'default':
                    default = 1
                elif w1 == 'machine' and w2:
                    host = w2.lower()
                    i = i + 1
                elif w1 == 'login' and w2:
                    user = w2
                    i = i + 1
                elif w1 == 'password' and w2:
                    passwd = w2
                    i = i + 1
                elif w1 == 'account' and w2:
                    acct = w2
                    i = i + 1
                elif w1 == 'macdef' and w2:
                    macro_name = w2
                    macro_lines = []
                    in_macro = 1
                    break
                i = i + 1

            if default:
                self.__defuser = user or self.__defuser
                self.__defpasswd = passwd or self.__defpasswd
                self.__defacct = acct or self.__defacct
            if host:
                if host in self.__hosts:
                    ouser, opasswd, oacct = self.__hosts[host]
                    user = user or ouser
                    passwd = passwd or opasswd
                    acct = acct or oacct
                self.__hosts[host] = (user, passwd, acct)

        fp.close()
        return

    def get_hosts(self):
        return self.__hosts.keys()

    def get_account(self, host):
        host = host.lower()
        user = passwd = acct = None
        if host in self.__hosts:
            user, passwd, acct = self.__hosts[host]
        user = user or self.__defuser
        passwd = passwd or self.__defpasswd
        acct = acct or self.__defacct
        return (user, passwd, acct)

    def get_macros(self):
        return self.__macros.keys()

    def get_macro(self, macro):
        return self.__macros[macro]


def test():
    if len(sys.argv) < 2:
        print test.__doc__
        sys.exit(0)
    debugging = 0
    rcfile = None
    while sys.argv[1] == '-d':
        debugging = debugging + 1
        del sys.argv[1]

    if sys.argv[1][:2] == '-r':
        rcfile = sys.argv[1][2:]
        del sys.argv[1]
    host = sys.argv[1]
    ftp = FTP(host)
    ftp.set_debuglevel(debugging)
    userid = passwd = acct = ''
    try:
        netrc = Netrc(rcfile)
    except IOError:
        if rcfile is not None:
            sys.stderr.write('Could not open account file -- using anonymous login.')
    else:
        try:
            userid, passwd, acct = netrc.get_account(host)
        except KeyError:
            sys.stderr.write('No account -- using anonymous login.')

    ftp.login(userid, passwd, acct)
    for file in sys.argv[2:]:
        if file[:2] == '-l':
            ftp.dir(file[2:])
        if file[:2] == '-d':
            cmd = 'CWD'
            if file[2:]:
                cmd = cmd + ' ' + file[2:]
            resp = ftp.sendcmd(cmd)
        if file == '-p':
            ftp.set_pasv(not ftp.passiveserver)
        ftp.retrbinary('RETR ' + file, sys.stdout.write, 1024)

    ftp.quit()
    return


if __name__ == '__main__':
    test()
