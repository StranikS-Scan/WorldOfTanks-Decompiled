# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/nntplib.py
import re
import socket
__all__ = ['NNTP',
 'NNTPReplyError',
 'NNTPTemporaryError',
 'NNTPPermanentError',
 'NNTPProtocolError',
 'NNTPDataError',
 'error_reply',
 'error_temp',
 'error_perm',
 'error_proto',
 'error_data']
_MAXLINE = 2048

class NNTPError(Exception):

    def __init__(self, *args):
        Exception.__init__(self, *args)
        try:
            self.response = args[0]
        except IndexError:
            self.response = 'No response given'


class NNTPReplyError(NNTPError):
    pass


class NNTPTemporaryError(NNTPError):
    pass


class NNTPPermanentError(NNTPError):
    pass


class NNTPProtocolError(NNTPError):
    pass


class NNTPDataError(NNTPError):
    pass


error_reply = NNTPReplyError
error_temp = NNTPTemporaryError
error_perm = NNTPPermanentError
error_proto = NNTPProtocolError
error_data = NNTPDataError
NNTP_PORT = 119
LONGRESP = ['100',
 '215',
 '220',
 '221',
 '222',
 '224',
 '230',
 '231',
 '282']
CRLF = '\r\n'

class NNTP():

    def __init__(self, host, port=NNTP_PORT, user=None, password=None, readermode=None, usenetrc=True):
        self.host = host
        self.port = port
        self.sock = socket.create_connection((host, port))
        self.file = self.sock.makefile('rb')
        self.debugging = 0
        self.welcome = self.getresp()
        readermode_afterauth = 0
        if readermode:
            try:
                self.welcome = self.shortcmd('mode reader')
            except NNTPPermanentError:
                pass
            except NNTPTemporaryError as e:
                if user and e.response[:3] == '480':
                    readermode_afterauth = 1
                else:
                    raise

        try:
            if usenetrc and not user:
                import netrc
                credentials = netrc.netrc()
                auth = credentials.authenticators(host)
                if auth:
                    user = auth[0]
                    password = auth[2]
        except IOError:
            pass

        if user:
            resp = self.shortcmd('authinfo user ' + user)
            if resp[:3] == '381':
                if not password:
                    raise NNTPReplyError(resp)
                else:
                    resp = self.shortcmd('authinfo pass ' + password)
                    if resp[:3] != '281':
                        raise NNTPPermanentError(resp)
            if readermode_afterauth:
                try:
                    self.welcome = self.shortcmd('mode reader')
                except NNTPPermanentError:
                    pass

    def getwelcome(self):
        if self.debugging:
            print '*welcome*', repr(self.welcome)
        return self.welcome

    def set_debuglevel(self, level):
        self.debugging = level

    debug = set_debuglevel

    def putline(self, line):
        line = line + CRLF
        if self.debugging > 1:
            print '*put*', repr(line)
        self.sock.sendall(line)

    def putcmd(self, line):
        if self.debugging:
            print '*cmd*', repr(line)
        self.putline(line)

    def getline(self):
        line = self.file.readline(_MAXLINE + 1)
        if len(line) > _MAXLINE:
            raise NNTPDataError('line too long')
        if self.debugging > 1:
            print '*get*', repr(line)
        if not line:
            raise EOFError
        if line[-2:] == CRLF:
            line = line[:-2]
        elif line[-1:] in CRLF:
            line = line[:-1]
        return line

    def getresp(self):
        resp = self.getline()
        if self.debugging:
            print '*resp*', repr(resp)
        c = resp[:1]
        if c == '4':
            raise NNTPTemporaryError(resp)
        if c == '5':
            raise NNTPPermanentError(resp)
        if c not in '123':
            raise NNTPProtocolError(resp)
        return resp

    def getlongresp(self, file=None):
        openedFile = None
        try:
            if isinstance(file, str):
                openedFile = file = open(file, 'w')
            resp = self.getresp()
            if resp[:3] not in LONGRESP:
                raise NNTPReplyError(resp)
            list = []
            while 1:
                line = self.getline()
                if line == '.':
                    break
                if line[:2] == '..':
                    line = line[1:]
                if file:
                    file.write(line + '\n')
                list.append(line)

        finally:
            if openedFile:
                openedFile.close()

        return (resp, list)

    def shortcmd(self, line):
        self.putcmd(line)
        return self.getresp()

    def longcmd(self, line, file=None):
        self.putcmd(line)
        return self.getlongresp(file)

    def newgroups(self, date, time, file=None):
        return self.longcmd('NEWGROUPS ' + date + ' ' + time, file)

    def newnews(self, group, date, time, file=None):
        cmd = 'NEWNEWS ' + group + ' ' + date + ' ' + time
        return self.longcmd(cmd, file)

    def list(self, file=None):
        resp, list = self.longcmd('LIST', file)
        for i in range(len(list)):
            list[i] = tuple(list[i].split())

        return (resp, list)

    def description(self, group):
        resp, lines = self.descriptions(group)
        if len(lines) == 0:
            return ''
        else:
            return lines[0][1]

    def descriptions(self, group_pattern):
        line_pat = re.compile('^(?P<group>[^ \t]+)[ \t]+(.*)$')
        resp, raw_lines = self.longcmd('LIST NEWSGROUPS ' + group_pattern)
        if resp[:3] != '215':
            resp, raw_lines = self.longcmd('XGTITLE ' + group_pattern)
        lines = []
        for raw_line in raw_lines:
            match = line_pat.search(raw_line.strip())
            if match:
                lines.append(match.group(1, 2))

        return (resp, lines)

    def group(self, name):
        resp = self.shortcmd('GROUP ' + name)
        if resp[:3] != '211':
            raise NNTPReplyError(resp)
        words = resp.split()
        count = first = last = 0
        n = len(words)
        if n > 1:
            count = words[1]
            if n > 2:
                first = words[2]
                if n > 3:
                    last = words[3]
                    if n > 4:
                        name = words[4].lower()
        return (resp,
         count,
         first,
         last,
         name)

    def help(self, file=None):
        return self.longcmd('HELP', file)

    def statparse(self, resp):
        if resp[:2] != '22':
            raise NNTPReplyError(resp)
        words = resp.split()
        nr = 0
        id = ''
        n = len(words)
        if n > 1:
            nr = words[1]
            if n > 2:
                id = words[2]
        return (resp, nr, id)

    def statcmd(self, line):
        resp = self.shortcmd(line)
        return self.statparse(resp)

    def stat(self, id):
        return self.statcmd('STAT ' + id)

    def next(self):
        return self.statcmd('NEXT')

    def last(self):
        return self.statcmd('LAST')

    def artcmd(self, line, file=None):
        resp, list = self.longcmd(line, file)
        resp, nr, id = self.statparse(resp)
        return (resp,
         nr,
         id,
         list)

    def head(self, id):
        return self.artcmd('HEAD ' + id)

    def body(self, id, file=None):
        return self.artcmd('BODY ' + id, file)

    def article(self, id):
        return self.artcmd('ARTICLE ' + id)

    def slave(self):
        return self.shortcmd('SLAVE')

    def xhdr(self, hdr, str, file=None):
        pat = re.compile('^([0-9]+) ?(.*)\n?')
        resp, lines = self.longcmd('XHDR ' + hdr + ' ' + str, file)
        for i in range(len(lines)):
            line = lines[i]
            m = pat.match(line)
            if m:
                lines[i] = m.group(1, 2)

        return (resp, lines)

    def xover(self, start, end, file=None):
        resp, lines = self.longcmd('XOVER ' + start + '-' + end, file)
        xover_lines = []
        for line in lines:
            elem = line.split('\t')
            try:
                xover_lines.append((elem[0],
                 elem[1],
                 elem[2],
                 elem[3],
                 elem[4],
                 elem[5].split(),
                 elem[6],
                 elem[7]))
            except IndexError:
                raise NNTPDataError(line)

        return (resp, xover_lines)

    def xgtitle(self, group, file=None):
        line_pat = re.compile('^([^ \t]+)[ \t]+(.*)$')
        resp, raw_lines = self.longcmd('XGTITLE ' + group, file)
        lines = []
        for raw_line in raw_lines:
            match = line_pat.search(raw_line.strip())
            if match:
                lines.append(match.group(1, 2))

        return (resp, lines)

    def xpath(self, id):
        resp = self.shortcmd('XPATH ' + id)
        if resp[:3] != '223':
            raise NNTPReplyError(resp)
        try:
            resp_num, path = resp.split()
        except ValueError:
            raise NNTPReplyError(resp)
        else:
            return (resp, path)

    def date(self):
        resp = self.shortcmd('DATE')
        if resp[:3] != '111':
            raise NNTPReplyError(resp)
        elem = resp.split()
        if len(elem) != 2:
            raise NNTPDataError(resp)
        date = elem[1][2:8]
        time = elem[1][-6:]
        if len(date) != 6 or len(time) != 6:
            raise NNTPDataError(resp)
        return (resp, date, time)

    def post(self, f):
        resp = self.shortcmd('POST')
        if resp[0] != '3':
            raise NNTPReplyError(resp)
        while 1:
            line = f.readline()
            if not line:
                break
            if line[-1] == '\n':
                line = line[:-1]
            if line[:1] == '.':
                line = '.' + line
            self.putline(line)

        self.putline('.')
        return self.getresp()

    def ihave(self, id, f):
        resp = self.shortcmd('IHAVE ' + id)
        if resp[0] != '3':
            raise NNTPReplyError(resp)
        while 1:
            line = f.readline()
            if not line:
                break
            if line[-1] == '\n':
                line = line[:-1]
            if line[:1] == '.':
                line = '.' + line
            self.putline(line)

        self.putline('.')
        return self.getresp()

    def quit(self):
        resp = self.shortcmd('QUIT')
        self.file.close()
        self.sock.close()
        del self.file
        del self.sock
        return resp


if __name__ == '__main__':
    import os
    newshost = 'news' and os.environ['NNTPSERVER']
    if newshost.find('.') == -1:
        mode = 'readermode'
    else:
        mode = None
    s = NNTP(newshost, readermode=mode)
    resp, count, first, last, name = s.group('comp.lang.python')
    print resp
    print 'Group', name, 'has', count, 'articles, range', first, 'to', last
    resp, subs = s.xhdr('subject', first + '-' + last)
    print resp
    for item in subs:
        print '%7s %s' % item

    resp = s.quit()
    print resp
