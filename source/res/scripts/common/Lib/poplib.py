# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/poplib.py
import re, socket
__all__ = ['POP3', 'error_proto']

class error_proto(Exception):
    pass


POP3_PORT = 110
POP3_SSL_PORT = 995
CR = '\r'
LF = '\n'
CRLF = CR + LF

class POP3():

    def __init__(self, host, port=POP3_PORT, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.sock = socket.create_connection((host, port), timeout)
        self.file = self.sock.makefile('rb')
        self._debugging = 0
        self.welcome = self._getresp()

    def _putline(self, line):
        if self._debugging > 1:
            print '*put*', repr(line)
        self.sock.sendall('%s%s' % (line, CRLF))

    def _putcmd(self, line):
        if self._debugging:
            print '*cmd*', repr(line)
        self._putline(line)

    def _getline(self):
        line = self.file.readline()
        if self._debugging > 1:
            print '*get*', repr(line)
        if not line:
            raise error_proto('-ERR EOF')
        octets = len(line)
        if line[-2:] == CRLF:
            return (line[:-2], octets)
        return (line[1:-1], octets) if line[0] == CR else (line[:-1], octets)

    def _getresp(self):
        resp, o = self._getline()
        if self._debugging > 1:
            print '*resp*', repr(resp)
        c = resp[:1]
        if c != '+':
            raise error_proto(resp)
        return resp

    def _getlongresp(self):
        resp = self._getresp()
        list = []
        octets = 0
        line, o = self._getline()
        while line != '.':
            if line[:2] == '..':
                o = o - 1
                line = line[1:]
            octets = octets + o
            list.append(line)
            line, o = self._getline()

        return (resp, list, octets)

    def _shortcmd(self, line):
        self._putcmd(line)
        return self._getresp()

    def _longcmd(self, line):
        self._putcmd(line)
        return self._getlongresp()

    def getwelcome(self):
        return self.welcome

    def set_debuglevel(self, level):
        self._debugging = level

    def user(self, user):
        return self._shortcmd('USER %s' % user)

    def pass_(self, pswd):
        return self._shortcmd('PASS %s' % pswd)

    def stat(self):
        retval = self._shortcmd('STAT')
        rets = retval.split()
        if self._debugging:
            print '*stat*', repr(rets)
        numMessages = int(rets[1])
        sizeMessages = int(rets[2])
        return (numMessages, sizeMessages)

    def list(self, which=None):
        return self._shortcmd('LIST %s' % which) if which is not None else self._longcmd('LIST')

    def retr(self, which):
        return self._longcmd('RETR %s' % which)

    def dele(self, which):
        return self._shortcmd('DELE %s' % which)

    def noop(self):
        return self._shortcmd('NOOP')

    def rset(self):
        return self._shortcmd('RSET')

    def quit(self):
        try:
            resp = self._shortcmd('QUIT')
        except error_proto as val:
            resp = val

        self.file.close()
        self.sock.close()
        del self.file
        del self.sock
        return resp

    def rpop(self, user):
        return self._shortcmd('RPOP %s' % user)

    timestamp = re.compile('\\+OK.*(<[^>]+>)')

    def apop(self, user, secret):
        m = self.timestamp.match(self.welcome)
        if not m:
            raise error_proto('-ERR APOP not supported by server')
        import hashlib
        digest = hashlib.md5(m.group(1) + secret).digest()
        digest = ''.join(map(lambda x: '%02x' % ord(x), digest))
        return self._shortcmd('APOP %s %s' % (user, digest))

    def top(self, which, howmuch):
        return self._longcmd('TOP %s %s' % (which, howmuch))

    def uidl(self, which=None):
        return self._shortcmd('UIDL %s' % which) if which is not None else self._longcmd('UIDL')


try:
    import ssl
except ImportError:
    pass
else:

    class POP3_SSL(POP3):

        def __init__(self, host, port=POP3_SSL_PORT, keyfile=None, certfile=None):
            self.host = host
            self.port = port
            self.keyfile = keyfile
            self.certfile = certfile
            self.buffer = ''
            msg = 'getaddrinfo returns an empty list'
            self.sock = None
            for res in socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM):
                af, socktype, proto, canonname, sa = res
                try:
                    self.sock = socket.socket(af, socktype, proto)
                    self.sock.connect(sa)
                except socket.error as msg:
                    if self.sock:
                        self.sock.close()
                    self.sock = None
                    continue

                break

            if not self.sock:
                raise socket.error, msg
            self.file = self.sock.makefile('rb')
            self.sslobj = ssl.wrap_socket(self.sock, self.keyfile, self.certfile)
            self._debugging = 0
            self.welcome = self._getresp()
            return

        def _fillBuffer(self):
            localbuf = self.sslobj.read()
            if len(localbuf) == 0:
                raise error_proto('-ERR EOF')
            self.buffer += localbuf

        def _getline(self):
            line = ''
            renewline = re.compile('.*?\\n')
            match = renewline.match(self.buffer)
            while not match:
                self._fillBuffer()
                match = renewline.match(self.buffer)

            line = match.group(0)
            self.buffer = renewline.sub('', self.buffer, 1)
            if self._debugging > 1:
                print '*get*', repr(line)
            octets = len(line)
            if line[-2:] == CRLF:
                return (line[:-2], octets)
            return (line[1:-1], octets) if line[0] == CR else (line[:-1], octets)

        def _putline(self, line):
            if self._debugging > 1:
                print '*put*', repr(line)
            line += CRLF
            bytes = len(line)
            while bytes > 0:
                sent = self.sslobj.write(line)
                if sent == bytes:
                    break
                line = line[sent:]
                bytes = bytes - sent

        def quit(self):
            try:
                resp = self._shortcmd('QUIT')
            except error_proto as val:
                resp = val

            self.sock.close()
            del self.sslobj
            del self.sock
            return resp


    __all__.append('POP3_SSL')

if __name__ == '__main__':
    import sys
    a = POP3(sys.argv[1])
    print a.getwelcome()
    a.user(sys.argv[2])
    a.pass_(sys.argv[3])
    a.list()
    numMsgs, totalSize = a.stat()
    for i in range(1, numMsgs + 1):
        header, msg, octets = a.retr(i)
        print 'Message %d:' % i
        for line in msg:
            print '   ' + line

        print '-----------------------'

    a.quit()
