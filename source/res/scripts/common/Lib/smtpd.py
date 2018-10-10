# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/smtpd.py
import sys
import os
import errno
import getopt
import time
import socket
import asyncore
import asynchat
__all__ = ['SMTPServer',
 'DebuggingServer',
 'PureProxy',
 'MailmanProxy']
program = sys.argv[0]
__version__ = 'Python SMTP proxy version 0.2'

class Devnull:

    def write(self, msg):
        pass

    def flush(self):
        pass


DEBUGSTREAM = Devnull()
NEWLINE = '\n'
EMPTYSTRING = ''
COMMASPACE = ', '

def usage(code, msg=''):
    print >> sys.stderr, __doc__ % globals()
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)


class SMTPChannel(asynchat.async_chat):
    COMMAND = 0
    DATA = 1

    def __init__(self, server, conn, addr):
        global DEBUGSTREAM
        asynchat.async_chat.__init__(self, conn)
        self.__server = server
        self.__conn = conn
        self.__addr = addr
        self.__line = []
        self.__state = self.COMMAND
        self.__greeting = 0
        self.__mailfrom = None
        self.__rcpttos = []
        self.__data = ''
        self.__fqdn = socket.getfqdn()
        try:
            self.__peer = conn.getpeername()
        except socket.error as err:
            self.close()
            if err[0] != errno.ENOTCONN:
                raise
            return

        print >> DEBUGSTREAM, 'Peer:', repr(self.__peer)
        self.push('220 %s %s' % (self.__fqdn, __version__))
        self.set_terminator('\r\n')
        return

    def push(self, msg):
        asynchat.async_chat.push(self, msg + '\r\n')

    def collect_incoming_data(self, data):
        self.__line.append(data)

    def found_terminator(self):
        line = EMPTYSTRING.join(self.__line)
        print >> DEBUGSTREAM, 'Data:', repr(line)
        self.__line = []
        if self.__state == self.COMMAND:
            if not line:
                self.push('500 Error: bad syntax')
                return
            method = None
            i = line.find(' ')
            if i < 0:
                command = line.upper()
                arg = None
            else:
                command = line[:i].upper()
                arg = line[i + 1:].strip()
            method = getattr(self, 'smtp_' + command, None)
            if not method:
                self.push('502 Error: command "%s" not implemented' % command)
                return
            method(arg)
            return
        elif self.__state != self.DATA:
            self.push('451 Internal confusion')
            return
        else:
            data = []
            for text in line.split('\r\n'):
                if text and text[0] == '.':
                    data.append(text[1:])
                data.append(text)

            self.__data = NEWLINE.join(data)
            status = self.__server.process_message(self.__peer, self.__mailfrom, self.__rcpttos, self.__data)
            self.__rcpttos = []
            self.__mailfrom = None
            self.__state = self.COMMAND
            self.set_terminator('\r\n')
            if not status:
                self.push('250 Ok')
            else:
                self.push(status)
            return

    def smtp_HELO(self, arg):
        if not arg:
            self.push('501 Syntax: HELO hostname')
            return
        if self.__greeting:
            self.push('503 Duplicate HELO/EHLO')
        else:
            self.__greeting = arg
            self.push('250 %s' % self.__fqdn)

    def smtp_NOOP(self, arg):
        if arg:
            self.push('501 Syntax: NOOP')
        else:
            self.push('250 Ok')

    def smtp_QUIT(self, arg):
        self.push('221 Bye')
        self.close_when_done()

    def __getaddr(self, keyword, arg):
        address = None
        keylen = len(keyword)
        if arg[:keylen].upper() == keyword:
            address = arg[keylen:].strip()
            if not address:
                pass
            elif address[0] == '<' and address[-1] == '>' and address != '<>':
                address = address[1:-1]
        return address

    def smtp_MAIL(self, arg):
        print >> DEBUGSTREAM, '===> MAIL', arg
        address = self.__getaddr('FROM:', arg) if arg else None
        if not address:
            self.push('501 Syntax: MAIL FROM:<address>')
            return
        elif self.__mailfrom:
            self.push('503 Error: nested MAIL command')
            return
        else:
            self.__mailfrom = address
            print >> DEBUGSTREAM, 'sender:', self.__mailfrom
            self.push('250 Ok')
            return

    def smtp_RCPT(self, arg):
        print >> DEBUGSTREAM, '===> RCPT', arg
        if not self.__mailfrom:
            self.push('503 Error: need MAIL command')
            return
        else:
            address = self.__getaddr('TO:', arg) if arg else None
            if not address:
                self.push('501 Syntax: RCPT TO: <address>')
                return
            self.__rcpttos.append(address)
            print >> DEBUGSTREAM, 'recips:', self.__rcpttos
            self.push('250 Ok')
            return

    def smtp_RSET(self, arg):
        if arg:
            self.push('501 Syntax: RSET')
            return
        else:
            self.__mailfrom = None
            self.__rcpttos = []
            self.__data = ''
            self.__state = self.COMMAND
            self.push('250 Ok')
            return

    def smtp_DATA(self, arg):
        if not self.__rcpttos:
            self.push('503 Error: need RCPT command')
            return
        if arg:
            self.push('501 Syntax: DATA')
            return
        self.__state = self.DATA
        self.set_terminator('\r\n.\r\n')
        self.push('354 End data with <CR><LF>.<CR><LF>')


class SMTPServer(asyncore.dispatcher):

    def __init__(self, localaddr, remoteaddr):
        self._localaddr = localaddr
        self._remoteaddr = remoteaddr
        asyncore.dispatcher.__init__(self)
        try:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind(localaddr)
            self.listen(5)
        except:
            self.close()
            raise
        else:
            print >> DEBUGSTREAM, '%s started at %s\n\tLocal addr: %s\n\tRemote addr:%s' % (self.__class__.__name__,
             time.ctime(time.time()),
             localaddr,
             remoteaddr)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            conn, addr = pair
            print >> DEBUGSTREAM, 'Incoming connection from %s' % repr(addr)
            channel = SMTPChannel(self, conn, addr)
        return

    def process_message(self, peer, mailfrom, rcpttos, data):
        raise NotImplementedError


class DebuggingServer(SMTPServer):

    def process_message(self, peer, mailfrom, rcpttos, data):
        inheaders = 1
        lines = data.split('\n')
        print '---------- MESSAGE FOLLOWS ----------'
        for line in lines:
            if inheaders and not line:
                print 'X-Peer:', peer[0]
                inheaders = 0
            print line

        print '------------ END MESSAGE ------------'


class PureProxy(SMTPServer):

    def process_message(self, peer, mailfrom, rcpttos, data):
        lines = data.split('\n')
        i = 0
        for line in lines:
            if not line:
                break
            i += 1

        lines.insert(i, 'X-Peer: %s' % peer[0])
        data = NEWLINE.join(lines)
        refused = self._deliver(mailfrom, rcpttos, data)
        print >> DEBUGSTREAM, 'we got some refusals:', refused

    def _deliver(self, mailfrom, rcpttos, data):
        import smtplib
        refused = {}
        try:
            s = smtplib.SMTP()
            s.connect(self._remoteaddr[0], self._remoteaddr[1])
            try:
                refused = s.sendmail(mailfrom, rcpttos, data)
            finally:
                s.quit()

        except smtplib.SMTPRecipientsRefused as e:
            print >> DEBUGSTREAM, 'got SMTPRecipientsRefused'
            refused = e.recipients
        except (socket.error, smtplib.SMTPException) as e:
            print >> DEBUGSTREAM, 'got', e.__class__
            errcode = getattr(e, 'smtp_code', -1)
            errmsg = getattr(e, 'smtp_error', 'ignore')
            for r in rcpttos:
                refused[r] = (errcode, errmsg)

        return refused


class MailmanProxy(PureProxy):

    def process_message(self, peer, mailfrom, rcpttos, data):
        from cStringIO import StringIO
        from Mailman import Utils
        from Mailman import Message
        from Mailman import MailList
        listnames = []
        for rcpt in rcpttos:
            local = rcpt.lower().split('@')[0]
            parts = local.split('-')
            if len(parts) > 2:
                continue
            listname = parts[0]
            if len(parts) == 2:
                command = parts[1]
            else:
                command = ''
            if not Utils.list_exists(listname) or command not in ('', 'admin', 'owner', 'request', 'join', 'leave'):
                continue
            listnames.append((rcpt, listname, command))

        for rcpt, listname, command in listnames:
            rcpttos.remove(rcpt)

        print >> DEBUGSTREAM, 'forwarding recips:', ' '.join(rcpttos)
        if rcpttos:
            refused = self._deliver(mailfrom, rcpttos, data)
            print >> DEBUGSTREAM, 'we got refusals:', refused
        mlists = {}
        s = StringIO(data)
        msg = Message.Message(s)
        if not msg.getheader('from'):
            msg['From'] = mailfrom
        if not msg.getheader('date'):
            msg['Date'] = time.ctime(time.time())
        for rcpt, listname, command in listnames:
            print >> DEBUGSTREAM, 'sending message to', rcpt
            mlist = mlists.get(listname)
            if not mlist:
                mlist = MailList.MailList(listname, lock=0)
                mlists[listname] = mlist
            if command == '':
                msg.Enqueue(mlist, tolist=1)
            if command == 'admin':
                msg.Enqueue(mlist, toadmin=1)
            if command == 'owner':
                msg.Enqueue(mlist, toowner=1)
            if command == 'request':
                msg.Enqueue(mlist, torequest=1)
            if command in ('join', 'leave'):
                if command == 'join':
                    msg['Subject'] = 'subscribe'
                else:
                    msg['Subject'] = 'unsubscribe'
                msg.Enqueue(mlist, torequest=1)


class Options:
    setuid = 1
    classname = 'PureProxy'


def parseargs():
    global DEBUGSTREAM
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'nVhc:d', ['class=',
         'nosetuid',
         'version',
         'help',
         'debug'])
    except getopt.error as e:
        usage(1, e)

    options = Options()
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        if opt in ('-V', '--version'):
            print >> sys.stderr, __version__
            sys.exit(0)
        if opt in ('-n', '--nosetuid'):
            options.setuid = 0
        if opt in ('-c', '--class'):
            options.classname = arg
        if opt in ('-d', '--debug'):
            DEBUGSTREAM = sys.stderr

    if len(args) < 1:
        localspec = 'localhost:8025'
        remotespec = 'localhost:25'
    elif len(args) < 2:
        localspec = args[0]
        remotespec = 'localhost:25'
    elif len(args) < 3:
        localspec = args[0]
        remotespec = args[1]
    else:
        usage(1, 'Invalid arguments: %s' % COMMASPACE.join(args))
    i = localspec.find(':')
    if i < 0:
        usage(1, 'Bad local spec: %s' % localspec)
    options.localhost = localspec[:i]
    try:
        options.localport = int(localspec[i + 1:])
    except ValueError:
        usage(1, 'Bad local port: %s' % localspec)

    i = remotespec.find(':')
    if i < 0:
        usage(1, 'Bad remote spec: %s' % remotespec)
    options.remotehost = remotespec[:i]
    try:
        options.remoteport = int(remotespec[i + 1:])
    except ValueError:
        usage(1, 'Bad remote port: %s' % remotespec)

    return options


if __name__ == '__main__':
    options = parseargs()
    classname = options.classname
    if '.' in classname:
        lastdot = classname.rfind('.')
        mod = __import__(classname[:lastdot], globals(), locals(), [''])
        classname = classname[lastdot + 1:]
    else:
        import __main__ as mod
    class_ = getattr(mod, classname)
    proxy = class_((options.localhost, options.localport), (options.remotehost, options.remoteport))
    if options.setuid:
        try:
            import pwd
        except ImportError:
            print >> sys.stderr, 'Cannot import module "pwd"; try running with -n option.'
            sys.exit(1)

        nobody = pwd.getpwnam('nobody')[2]
        try:
            os.setuid(nobody)
        except OSError as e:
            if e.errno != errno.EPERM:
                raise
            print >> sys.stderr, 'Cannot setuid "nobody"; try running with -n option.'
            sys.exit(1)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
