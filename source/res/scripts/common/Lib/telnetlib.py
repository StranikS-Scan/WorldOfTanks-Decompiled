# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/telnetlib.py
import errno
import sys
import socket
import select
__all__ = ['Telnet']
DEBUGLEVEL = 0
TELNET_PORT = 23
IAC = chr(255)
DONT = chr(254)
DO = chr(253)
WONT = chr(252)
WILL = chr(251)
theNULL = chr(0)
SE = chr(240)
NOP = chr(241)
DM = chr(242)
BRK = chr(243)
IP = chr(244)
AO = chr(245)
AYT = chr(246)
EC = chr(247)
EL = chr(248)
GA = chr(249)
SB = chr(250)
BINARY = chr(0)
ECHO = chr(1)
RCP = chr(2)
SGA = chr(3)
NAMS = chr(4)
STATUS = chr(5)
TM = chr(6)
RCTE = chr(7)
NAOL = chr(8)
NAOP = chr(9)
NAOCRD = chr(10)
NAOHTS = chr(11)
NAOHTD = chr(12)
NAOFFD = chr(13)
NAOVTS = chr(14)
NAOVTD = chr(15)
NAOLFD = chr(16)
XASCII = chr(17)
LOGOUT = chr(18)
BM = chr(19)
DET = chr(20)
SUPDUP = chr(21)
SUPDUPOUTPUT = chr(22)
SNDLOC = chr(23)
TTYPE = chr(24)
EOR = chr(25)
TUID = chr(26)
OUTMRK = chr(27)
TTYLOC = chr(28)
VT3270REGIME = chr(29)
X3PAD = chr(30)
NAWS = chr(31)
TSPEED = chr(32)
LFLOW = chr(33)
LINEMODE = chr(34)
XDISPLOC = chr(35)
OLD_ENVIRON = chr(36)
AUTHENTICATION = chr(37)
ENCRYPT = chr(38)
NEW_ENVIRON = chr(39)
TN3270E = chr(40)
XAUTH = chr(41)
CHARSET = chr(42)
RSP = chr(43)
COM_PORT_OPTION = chr(44)
SUPPRESS_LOCAL_ECHO = chr(45)
TLS = chr(46)
KERMIT = chr(47)
SEND_URL = chr(48)
FORWARD_X = chr(49)
PRAGMA_LOGON = chr(138)
SSPI_LOGON = chr(139)
PRAGMA_HEARTBEAT = chr(140)
EXOPL = chr(255)
NOOPT = chr(0)

class Telnet():

    def __init__(self, host=None, port=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.debuglevel = DEBUGLEVEL
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.rawq = ''
        self.irawq = 0
        self.cookedq = ''
        self.eof = 0
        self.iacseq = ''
        self.sb = 0
        self.sbdataq = ''
        self.option_callback = None
        self._has_poll = hasattr(select, 'poll')
        if host is not None:
            self.open(host, port, timeout)
        return

    def open(self, host, port=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.eof = 0
        if not port:
            port = TELNET_PORT
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = socket.create_connection((host, port), timeout)

    def __del__(self):
        self.close()

    def msg(self, msg, *args):
        if self.debuglevel > 0:
            print 'Telnet(%s,%s):' % (self.host, self.port),
            if args:
                print msg % args
            else:
                print msg

    def set_debuglevel(self, debuglevel):
        self.debuglevel = debuglevel

    def close(self):
        if self.sock:
            self.sock.close()
        self.sock = 0
        self.eof = 1
        self.iacseq = ''
        self.sb = 0

    def get_socket(self):
        return self.sock

    def fileno(self):
        return self.sock.fileno()

    def write(self, buffer):
        if IAC in buffer:
            buffer = buffer.replace(IAC, IAC + IAC)
        self.msg('send %r', buffer)
        self.sock.sendall(buffer)

    def read_until(self, match, timeout=None):
        if self._has_poll:
            return self._read_until_with_poll(match, timeout)
        else:
            return self._read_until_with_select(match, timeout)

    def _read_until_with_poll(self, match, timeout):
        n = len(match)
        call_timeout = timeout
        if timeout is not None:
            from time import time
            time_start = time()
        self.process_rawq()
        i = self.cookedq.find(match)
        if i < 0:
            poller = select.poll()
            poll_in_or_priority_flags = select.POLLIN | select.POLLPRI
            poller.register(self, poll_in_or_priority_flags)
            while i < 0 and not self.eof:
                try:
                    ready = poller.poll(None if timeout is None else 1000 * call_timeout)
                except select.error as e:
                    if e.errno == errno.EINTR:
                        if timeout is not None:
                            elapsed = time() - time_start
                            call_timeout = timeout - elapsed
                        continue
                    raise

                for fd, mode in ready:
                    if mode & poll_in_or_priority_flags:
                        i = max(0, len(self.cookedq) - n)
                        self.fill_rawq()
                        self.process_rawq()
                        i = self.cookedq.find(match, i)

                if timeout is not None:
                    elapsed = time() - time_start
                    if elapsed >= timeout:
                        break
                    call_timeout = timeout - elapsed

            poller.unregister(self)
        if i >= 0:
            i = i + n
            buf = self.cookedq[:i]
            self.cookedq = self.cookedq[i:]
            return buf
        else:
            return self.read_very_lazy()

    def _read_until_with_select(self, match, timeout=None):
        n = len(match)
        self.process_rawq()
        i = self.cookedq.find(match)
        if i >= 0:
            i = i + n
            buf = self.cookedq[:i]
            self.cookedq = self.cookedq[i:]
            return buf
        else:
            s_reply = ([self], [], [])
            s_args = s_reply
            if timeout is not None:
                s_args = s_args + (timeout,)
                from time import time
                time_start = time()
            while not self.eof and select.select(*s_args) == s_reply:
                i = max(0, len(self.cookedq) - n)
                self.fill_rawq()
                self.process_rawq()
                i = self.cookedq.find(match, i)
                if i >= 0:
                    i = i + n
                    buf = self.cookedq[:i]
                    self.cookedq = self.cookedq[i:]
                    return buf
                if timeout is not None:
                    elapsed = time() - time_start
                    if elapsed >= timeout:
                        break
                    s_args = s_reply + (timeout - elapsed,)

            return self.read_very_lazy()

    def read_all(self):
        self.process_rawq()
        while not self.eof:
            self.fill_rawq()
            self.process_rawq()

        buf = self.cookedq
        self.cookedq = ''
        return buf

    def read_some(self):
        self.process_rawq()
        while not self.cookedq and not self.eof:
            self.fill_rawq()
            self.process_rawq()

        buf = self.cookedq
        self.cookedq = ''
        return buf

    def read_very_eager(self):
        self.process_rawq()
        while not self.eof and self.sock_avail():
            self.fill_rawq()
            self.process_rawq()

        return self.read_very_lazy()

    def read_eager(self):
        self.process_rawq()
        while not self.cookedq and not self.eof and self.sock_avail():
            self.fill_rawq()
            self.process_rawq()

        return self.read_very_lazy()

    def read_lazy(self):
        self.process_rawq()
        return self.read_very_lazy()

    def read_very_lazy(self):
        buf = self.cookedq
        self.cookedq = ''
        if not buf and self.eof and not self.rawq:
            raise EOFError, 'telnet connection closed'
        return buf

    def read_sb_data(self):
        buf = self.sbdataq
        self.sbdataq = ''
        return buf

    def set_option_negotiation_callback(self, callback):
        self.option_callback = callback

    def process_rawq(self):
        buf = ['', '']
        try:
            while self.rawq:
                c = self.rawq_getchar()
                if not self.iacseq:
                    if c == theNULL:
                        continue
                    if c == '\x11':
                        continue
                    if c != IAC:
                        buf[self.sb] = buf[self.sb] + c
                        continue
                    else:
                        self.iacseq += c
                if len(self.iacseq) == 1:
                    if c in (DO,
                     DONT,
                     WILL,
                     WONT):
                        self.iacseq += c
                        continue
                    self.iacseq = ''
                    if c == IAC:
                        buf[self.sb] = buf[self.sb] + c
                    else:
                        if c == SB:
                            self.sb = 1
                            self.sbdataq = ''
                        elif c == SE:
                            self.sb = 0
                            self.sbdataq = self.sbdataq + buf[1]
                            buf[1] = ''
                        if self.option_callback:
                            self.option_callback(self.sock, c, NOOPT)
                        else:
                            self.msg('IAC %d not recognized' % ord(c))
                if len(self.iacseq) == 2:
                    cmd = self.iacseq[1]
                    self.iacseq = ''
                    opt = c
                    if cmd in (DO, DONT):
                        self.msg('IAC %s %d', cmd == DO and 'DO' or 'DONT', ord(opt))
                        if self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        else:
                            self.sock.sendall(IAC + WONT + opt)
                    elif cmd in (WILL, WONT):
                        self.msg('IAC %s %d', cmd == WILL and 'WILL' or 'WONT', ord(opt))
                        if self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        else:
                            self.sock.sendall(IAC + DONT + opt)

        except EOFError:
            self.iacseq = ''
            self.sb = 0

        self.cookedq = self.cookedq + buf[0]
        self.sbdataq = self.sbdataq + buf[1]

    def rawq_getchar(self):
        if not self.rawq:
            self.fill_rawq()
            if self.eof:
                raise EOFError
        c = self.rawq[self.irawq]
        self.irawq = self.irawq + 1
        if self.irawq >= len(self.rawq):
            self.rawq = ''
            self.irawq = 0
        return c

    def fill_rawq(self):
        if self.irawq >= len(self.rawq):
            self.rawq = ''
            self.irawq = 0
        buf = self.sock.recv(50)
        self.msg('recv %r', buf)
        self.eof = not buf
        self.rawq = self.rawq + buf

    def sock_avail(self):
        return select.select([self], [], [], 0) == ([self], [], [])

    def interact(self):
        if sys.platform == 'win32':
            self.mt_interact()
            return
        while 1:
            rfd, wfd, xfd = select.select([self, sys.stdin], [], [])
            if self in rfd:
                try:
                    text = self.read_eager()
                except EOFError:
                    print '*** Connection closed by remote host ***'
                    break

                if text:
                    sys.stdout.write(text)
                    sys.stdout.flush()
            if sys.stdin in rfd:
                line = sys.stdin.readline()
                if not line:
                    break
                self.write(line)

    def mt_interact(self):
        import thread
        thread.start_new_thread(self.listener, ())
        while 1:
            line = sys.stdin.readline()
            if not line:
                break
            self.write(line)

    def listener(self):
        while 1:
            try:
                data = self.read_eager()
            except EOFError:
                print '*** Connection closed by remote host ***'
                return

            if data:
                sys.stdout.write(data)
            sys.stdout.flush()

    def expect(self, list, timeout=None):
        if self._has_poll:
            return self._expect_with_poll(list, timeout)
        else:
            return self._expect_with_select(list, timeout)

    def _expect_with_poll(self, expect_list, timeout=None):
        re = None
        expect_list = expect_list[:]
        indices = range(len(expect_list))
        for i in indices:
            if not hasattr(expect_list[i], 'search'):
                if not re:
                    import re
                expect_list[i] = re.compile(expect_list[i])

        call_timeout = timeout
        if timeout is not None:
            from time import time
            time_start = time()
        self.process_rawq()
        m = None
        for i in indices:
            m = expect_list[i].search(self.cookedq)
            if m:
                e = m.end()
                text = self.cookedq[:e]
                self.cookedq = self.cookedq[e:]
                break

        if not m:
            poller = select.poll()
            poll_in_or_priority_flags = select.POLLIN | select.POLLPRI
            poller.register(self, poll_in_or_priority_flags)
            while not m and not self.eof:
                try:
                    ready = poller.poll(None if timeout is None else 1000 * call_timeout)
                except select.error as e:
                    if e.errno == errno.EINTR:
                        if timeout is not None:
                            elapsed = time() - time_start
                            call_timeout = timeout - elapsed
                        continue
                    raise

                for fd, mode in ready:
                    if mode & poll_in_or_priority_flags:
                        self.fill_rawq()
                        self.process_rawq()
                        for i in indices:
                            m = expect_list[i].search(self.cookedq)
                            if m:
                                e = m.end()
                                text = self.cookedq[:e]
                                self.cookedq = self.cookedq[e:]
                                break

                if timeout is not None:
                    elapsed = time() - time_start
                    if elapsed >= timeout:
                        break
                    call_timeout = timeout - elapsed

            poller.unregister(self)
        if m:
            return (i, m, text)
        else:
            text = self.read_very_lazy()
            if not text and self.eof:
                raise EOFError
            return (-1, None, text)

    def _expect_with_select(self, list, timeout=None):
        re = None
        list = list[:]
        indices = range(len(list))
        for i in indices:
            if not hasattr(list[i], 'search'):
                if not re:
                    import re
                list[i] = re.compile(list[i])

        if timeout is not None:
            from time import time
            time_start = time()
        while 1:
            self.process_rawq()
            for i in indices:
                m = list[i].search(self.cookedq)
                if m:
                    e = m.end()
                    text = self.cookedq[:e]
                    self.cookedq = self.cookedq[e:]
                    return (i, m, text)

            if self.eof:
                break
            if timeout is not None:
                elapsed = time() - time_start
                if elapsed >= timeout:
                    break
                s_args = ([self.fileno()],
                 [],
                 [],
                 timeout - elapsed)
                r, w, x = select.select(*s_args)
                if not r:
                    break
            self.fill_rawq()

        text = self.read_very_lazy()
        if not text and self.eof:
            raise EOFError
        return (-1, None, text)


def test():
    debuglevel = 0
    while sys.argv[1:] and sys.argv[1] == '-d':
        debuglevel = debuglevel + 1
        del sys.argv[1]

    host = 'localhost'
    if sys.argv[1:]:
        host = sys.argv[1]
    port = 0
    if sys.argv[2:]:
        portstr = sys.argv[2]
        try:
            port = int(portstr)
        except ValueError:
            port = socket.getservbyname(portstr, 'tcp')

    tn = Telnet()
    tn.set_debuglevel(debuglevel)
    tn.open(host, port, timeout=0.5)
    tn.interact()
    tn.close()


if __name__ == '__main__':
    test()
