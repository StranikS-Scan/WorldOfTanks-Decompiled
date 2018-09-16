# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/logging/handlers.py
import errno, logging, socket, os, cPickle, struct, time, re
from stat import ST_DEV, ST_INO, ST_MTIME
try:
    import codecs
except ImportError:
    codecs = None

try:
    unicode
    _unicode = True
except NameError:
    _unicode = False

DEFAULT_TCP_LOGGING_PORT = 9020
DEFAULT_UDP_LOGGING_PORT = 9021
DEFAULT_HTTP_LOGGING_PORT = 9022
DEFAULT_SOAP_LOGGING_PORT = 9023
SYSLOG_UDP_PORT = 514
SYSLOG_TCP_PORT = 514
_MIDNIGHT = 86400

class BaseRotatingHandler(logging.FileHandler):

    def __init__(self, filename, mode, encoding=None, delay=0):
        if codecs is None:
            encoding = None
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.mode = mode
        self.encoding = encoding
        return

    def emit(self, record):
        try:
            if self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class RotatingFileHandler(BaseRotatingHandler):

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        if maxBytes > 0:
            mode = 'a'
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = '%s.%d' % (self.baseFilename, i)
                dfn = '%s.%d' % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)

            dfn = self.baseFilename + '.1'
            if os.path.exists(dfn):
                os.remove(dfn)
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()
        return

    def shouldRollover(self, record):
        if self.stream is None:
            self.stream = self._open()
        if self.maxBytes > 0:
            msg = '%s\n' % self.format(record)
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        return 0


class TimedRotatingFileHandler(BaseRotatingHandler):

    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)
        self.when = when.upper()
        self.backupCount = backupCount
        self.utc = utc
        if self.when == 'S':
            self.interval = 1
            self.suffix = '%Y-%m-%d_%H-%M-%S'
            self.extMatch = '^\\d{4}-\\d{2}-\\d{2}_\\d{2}-\\d{2}-\\d{2}$'
        elif self.when == 'M':
            self.interval = 60
            self.suffix = '%Y-%m-%d_%H-%M'
            self.extMatch = '^\\d{4}-\\d{2}-\\d{2}_\\d{2}-\\d{2}$'
        elif self.when == 'H':
            self.interval = 3600
            self.suffix = '%Y-%m-%d_%H'
            self.extMatch = '^\\d{4}-\\d{2}-\\d{2}_\\d{2}$'
        elif self.when == 'D' or self.when == 'MIDNIGHT':
            self.interval = 86400
            self.suffix = '%Y-%m-%d'
            self.extMatch = '^\\d{4}-\\d{2}-\\d{2}$'
        elif self.when.startswith('W'):
            self.interval = 604800
            if len(self.when) != 2:
                raise ValueError('You must specify a day for weekly rollover from 0 to 6 (0 is Monday): %s' % self.when)
            if self.when[1] < '0' or self.when[1] > '6':
                raise ValueError('Invalid day specified for weekly rollover: %s' % self.when)
            self.dayOfWeek = int(self.when[1])
            self.suffix = '%Y-%m-%d'
            self.extMatch = '^\\d{4}-\\d{2}-\\d{2}$'
        else:
            raise ValueError('Invalid rollover interval specified: %s' % self.when)
        self.extMatch = re.compile(self.extMatch)
        self.interval = self.interval * interval
        if os.path.exists(filename):
            t = os.stat(filename)[ST_MTIME]
        else:
            t = int(time.time())
        self.rolloverAt = self.computeRollover(t)

    def computeRollover(self, currentTime):
        result = currentTime + self.interval
        if self.when == 'MIDNIGHT' or self.when.startswith('W'):
            if self.utc:
                t = time.gmtime(currentTime)
            else:
                t = time.localtime(currentTime)
            currentHour = t[3]
            currentMinute = t[4]
            currentSecond = t[5]
            r = _MIDNIGHT - ((currentHour * 60 + currentMinute) * 60 + currentSecond)
            result = currentTime + r
            if self.when.startswith('W'):
                day = t[6]
                if day != self.dayOfWeek:
                    if day < self.dayOfWeek:
                        daysToWait = self.dayOfWeek - day
                    else:
                        daysToWait = 6 - day + self.dayOfWeek + 1
                    newRolloverAt = result + daysToWait * 86400
                    if not self.utc:
                        dstNow = t[-1]
                        dstAtRollover = time.localtime(newRolloverAt)[-1]
                        if dstNow != dstAtRollover:
                            if not dstNow:
                                addend = -3600
                            else:
                                addend = 3600
                            newRolloverAt += addend
                    result = newRolloverAt
        return result

    def shouldRollover(self, record):
        t = int(time.time())
        return 1 if t >= self.rolloverAt else 0

    def getFilesToDelete(self):
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + '.'
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))

        result.sort()
        if len(result) < self.backupCount:
            result = []
        else:
            result = result[:len(result) - self.backupCount]
        return result

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + '.' + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:
                    addend = -3600
                else:
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
        return


class WatchedFileHandler(logging.FileHandler):

    def __init__(self, filename, mode='a', encoding=None, delay=0):
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.dev, self.ino = (-1, -1)
        self._statstream()

    def _statstream(self):
        if self.stream:
            sres = os.fstat(self.stream.fileno())
            self.dev, self.ino = sres[ST_DEV], sres[ST_INO]

    def emit(self, record):
        try:
            sres = os.stat(self.baseFilename)
        except OSError as err:
            if err.errno == errno.ENOENT:
                sres = None
            else:
                raise

        if not sres or sres[ST_DEV] != self.dev or sres[ST_INO] != self.ino:
            if self.stream is not None:
                self.stream.flush()
                self.stream.close()
                self.stream = self._open()
                self._statstream()
        logging.FileHandler.emit(self, record)
        return


class SocketHandler(logging.Handler):

    def __init__(self, host, port):
        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        self.sock = None
        self.closeOnError = 0
        self.retryTime = None
        self.retryStart = 1.0
        self.retryMax = 30.0
        self.retryFactor = 2.0
        return

    def makeSocket(self, timeout=1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if hasattr(s, 'settimeout'):
            s.settimeout(timeout)
        s.connect((self.host, self.port))
        return s

    def createSocket(self):
        now = time.time()
        if self.retryTime is None:
            attempt = 1
        else:
            attempt = now >= self.retryTime
        if attempt:
            try:
                self.sock = self.makeSocket()
                self.retryTime = None
            except socket.error:
                if self.retryTime is None:
                    self.retryPeriod = self.retryStart
                else:
                    self.retryPeriod = self.retryPeriod * self.retryFactor
                    if self.retryPeriod > self.retryMax:
                        self.retryPeriod = self.retryMax
                self.retryTime = now + self.retryPeriod

        return

    def send(self, s):
        if self.sock is None:
            self.createSocket()
        if self.sock:
            try:
                if hasattr(self.sock, 'sendall'):
                    self.sock.sendall(s)
                else:
                    sentsofar = 0
                    left = len(s)
                    while left > 0:
                        sent = self.sock.send(s[sentsofar:])
                        sentsofar = sentsofar + sent
                        left = left - sent

            except socket.error:
                self.sock.close()
                self.sock = None

        return

    def makePickle(self, record):
        ei = record.exc_info
        if ei:
            dummy = self.format(record)
            record.exc_info = None
        d = dict(record.__dict__)
        d['msg'] = record.getMessage()
        d['args'] = None
        s = cPickle.dumps(d, 1)
        if ei:
            record.exc_info = ei
        slen = struct.pack('>L', len(s))
        return slen + s

    def handleError(self, record):
        if self.closeOnError and self.sock:
            self.sock.close()
            self.sock = None
        else:
            logging.Handler.handleError(self, record)
        return

    def emit(self, record):
        try:
            s = self.makePickle(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self.acquire()
        try:
            if self.sock:
                self.sock.close()
                self.sock = None
        finally:
            self.release()

        logging.Handler.close(self)
        return


class DatagramHandler(SocketHandler):

    def __init__(self, host, port):
        SocketHandler.__init__(self, host, port)
        self.closeOnError = 0

    def makeSocket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return s

    def send(self, s):
        if self.sock is None:
            self.createSocket()
        self.sock.sendto(s, (self.host, self.port))
        return


class SysLogHandler(logging.Handler):
    LOG_EMERG = 0
    LOG_ALERT = 1
    LOG_CRIT = 2
    LOG_ERR = 3
    LOG_WARNING = 4
    LOG_NOTICE = 5
    LOG_INFO = 6
    LOG_DEBUG = 7
    LOG_KERN = 0
    LOG_USER = 1
    LOG_MAIL = 2
    LOG_DAEMON = 3
    LOG_AUTH = 4
    LOG_SYSLOG = 5
    LOG_LPR = 6
    LOG_NEWS = 7
    LOG_UUCP = 8
    LOG_CRON = 9
    LOG_AUTHPRIV = 10
    LOG_FTP = 11
    LOG_LOCAL0 = 16
    LOG_LOCAL1 = 17
    LOG_LOCAL2 = 18
    LOG_LOCAL3 = 19
    LOG_LOCAL4 = 20
    LOG_LOCAL5 = 21
    LOG_LOCAL6 = 22
    LOG_LOCAL7 = 23
    priority_names = {'alert': LOG_ALERT,
     'crit': LOG_CRIT,
     'critical': LOG_CRIT,
     'debug': LOG_DEBUG,
     'emerg': LOG_EMERG,
     'err': LOG_ERR,
     'error': LOG_ERR,
     'info': LOG_INFO,
     'notice': LOG_NOTICE,
     'panic': LOG_EMERG,
     'warn': LOG_WARNING,
     'warning': LOG_WARNING}
    facility_names = {'auth': LOG_AUTH,
     'authpriv': LOG_AUTHPRIV,
     'cron': LOG_CRON,
     'daemon': LOG_DAEMON,
     'ftp': LOG_FTP,
     'kern': LOG_KERN,
     'lpr': LOG_LPR,
     'mail': LOG_MAIL,
     'news': LOG_NEWS,
     'security': LOG_AUTH,
     'syslog': LOG_SYSLOG,
     'user': LOG_USER,
     'uucp': LOG_UUCP,
     'local0': LOG_LOCAL0,
     'local1': LOG_LOCAL1,
     'local2': LOG_LOCAL2,
     'local3': LOG_LOCAL3,
     'local4': LOG_LOCAL4,
     'local5': LOG_LOCAL5,
     'local6': LOG_LOCAL6,
     'local7': LOG_LOCAL7}
    priority_map = {'DEBUG': 'debug',
     'INFO': 'info',
     'WARNING': 'warning',
     'ERROR': 'error',
     'CRITICAL': 'critical'}

    def __init__(self, address=('localhost', SYSLOG_UDP_PORT), facility=LOG_USER, socktype=None):
        logging.Handler.__init__(self)
        self.address = address
        self.facility = facility
        self.socktype = socktype
        if isinstance(address, basestring):
            self.unixsocket = 1
            self._connect_unixsocket(address)
        else:
            self.unixsocket = 0
            if socktype is None:
                socktype = socket.SOCK_DGRAM
            self.socket = socket.socket(socket.AF_INET, socktype)
            if socktype == socket.SOCK_STREAM:
                self.socket.connect(address)
            self.socktype = socktype
        self.formatter = None
        return

    def _connect_unixsocket(self, address):
        use_socktype = self.socktype
        if use_socktype is None:
            use_socktype = socket.SOCK_DGRAM
        self.socket = socket.socket(socket.AF_UNIX, use_socktype)
        try:
            self.socket.connect(address)
            self.socktype = use_socktype
        except socket.error:
            self.socket.close()
            if self.socktype is not None:
                raise
            use_socktype = socket.SOCK_STREAM
            self.socket = socket.socket(socket.AF_UNIX, use_socktype)
            try:
                self.socket.connect(address)
                self.socktype = use_socktype
            except socket.error:
                self.socket.close()
                raise

        return

    log_format_string = '<%d>%s\x00'

    def encodePriority(self, facility, priority):
        if isinstance(facility, basestring):
            facility = self.facility_names[facility]
        if isinstance(priority, basestring):
            priority = self.priority_names[priority]
        return facility << 3 | priority

    def close(self):
        self.acquire()
        try:
            if self.unixsocket:
                self.socket.close()
        finally:
            self.release()

        logging.Handler.close(self)

    def mapPriority(self, levelName):
        return self.priority_map.get(levelName, 'warning')

    def emit(self, record):
        msg = self.format(record) + '\x00'
        prio = '<%d>' % self.encodePriority(self.facility, self.mapPriority(record.levelname))
        if type(msg) is unicode:
            msg = msg.encode('utf-8')
        msg = prio + msg
        try:
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except socket.error:
                    self.socket.close()
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)

            elif self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class SMTPHandler(logging.Handler):

    def __init__(self, mailhost, fromaddr, toaddrs, subject, credentials=None, secure=None):
        logging.Handler.__init__(self)
        if isinstance(mailhost, tuple):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost, self.mailport = mailhost, None
        if isinstance(credentials, tuple):
            self.username, self.password = credentials
        else:
            self.username = None
        self.fromaddr = fromaddr
        if isinstance(toaddrs, basestring):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure
        self._timeout = 5.0
        return

    def getSubject(self, record):
        return self.subject

    def emit(self, record):
        try:
            import smtplib
            from email.utils import formatdate
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port, timeout=self._timeout)
            msg = self.format(record)
            msg = 'From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s' % (self.fromaddr,
             ','.join(self.toaddrs),
             self.getSubject(record),
             formatdate(),
             msg)
            if self.username:
                if self.secure is not None:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

        return


class NTEventLogHandler(logging.Handler):

    def __init__(self, appname, dllname=None, logtype='Application'):
        logging.Handler.__init__(self)
        try:
            import win32evtlogutil, win32evtlog
            self.appname = appname
            self._welu = win32evtlogutil
            if not dllname:
                dllname = os.path.split(self._welu.__file__)
                dllname = os.path.split(dllname[0])
                dllname = os.path.join(dllname[0], 'win32service.pyd')
            self.dllname = dllname
            self.logtype = logtype
            self._welu.AddSourceToRegistry(appname, dllname, logtype)
            self.deftype = win32evtlog.EVENTLOG_ERROR_TYPE
            self.typemap = {logging.DEBUG: win32evtlog.EVENTLOG_INFORMATION_TYPE,
             logging.INFO: win32evtlog.EVENTLOG_INFORMATION_TYPE,
             logging.WARNING: win32evtlog.EVENTLOG_WARNING_TYPE,
             logging.ERROR: win32evtlog.EVENTLOG_ERROR_TYPE,
             logging.CRITICAL: win32evtlog.EVENTLOG_ERROR_TYPE}
        except ImportError:
            print 'The Python Win32 extensions for NT (service, event logging) appear not to be available.'
            self._welu = None

        return

    def getMessageID(self, record):
        pass

    def getEventCategory(self, record):
        pass

    def getEventType(self, record):
        return self.typemap.get(record.levelno, self.deftype)

    def emit(self, record):
        if self._welu:
            try:
                id = self.getMessageID(record)
                cat = self.getEventCategory(record)
                type = self.getEventType(record)
                msg = self.format(record)
                self._welu.ReportEvent(self.appname, id, cat, type, [msg])
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    def close(self):
        logging.Handler.close(self)


class HTTPHandler(logging.Handler):

    def __init__(self, host, url, method='GET'):
        logging.Handler.__init__(self)
        method = method.upper()
        if method not in ('GET', 'POST'):
            raise ValueError('method must be GET or POST')
        self.host = host
        self.url = url
        self.method = method

    def mapLogRecord(self, record):
        return record.__dict__

    def emit(self, record):
        try:
            import httplib, urllib
            host = self.host
            h = httplib.HTTP(host)
            url = self.url
            data = urllib.urlencode(self.mapLogRecord(record))
            if self.method == 'GET':
                if url.find('?') >= 0:
                    sep = '&'
                else:
                    sep = '?'
                url = url + '%c%s' % (sep, data)
            h.putrequest(self.method, url)
            i = host.find(':')
            if i >= 0:
                host = host[:i]
            h.putheader('Host', host)
            if self.method == 'POST':
                h.putheader('Content-type', 'application/x-www-form-urlencoded')
                h.putheader('Content-length', str(len(data)))
            h.endheaders(data if self.method == 'POST' else None)
            h.getreply()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

        return


class BufferingHandler(logging.Handler):

    def __init__(self, capacity):
        logging.Handler.__init__(self)
        self.capacity = capacity
        self.buffer = []

    def shouldFlush(self, record):
        return len(self.buffer) >= self.capacity

    def emit(self, record):
        self.buffer.append(record)
        if self.shouldFlush(record):
            self.flush()

    def flush(self):
        self.acquire()
        try:
            self.buffer = []
        finally:
            self.release()

    def close(self):
        self.flush()
        logging.Handler.close(self)


class MemoryHandler(BufferingHandler):

    def __init__(self, capacity, flushLevel=logging.ERROR, target=None):
        BufferingHandler.__init__(self, capacity)
        self.flushLevel = flushLevel
        self.target = target

    def shouldFlush(self, record):
        return len(self.buffer) >= self.capacity or record.levelno >= self.flushLevel

    def setTarget(self, target):
        self.target = target

    def flush(self):
        self.acquire()
        try:
            if self.target:
                for record in self.buffer:
                    self.target.handle(record)

                self.buffer = []
        finally:
            self.release()

    def close(self):
        self.flush()
        self.acquire()
        try:
            self.target = None
            BufferingHandler.close(self)
        finally:
            self.release()

        return
