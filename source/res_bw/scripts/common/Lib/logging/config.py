# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/logging/config.py
# Compiled at: 2010-05-25 20:46:16
"""
Configuration functions for the logging package for Python. The core package
is based on PEP 282 and comments thereto in comp.lang.python, and influenced
by Apache's log4j system.

Should work under Python versions >= 1.5.2, except that source line
information is not available unless 'sys._getframe()' is.

Copyright (C) 2001-2008 Vinay Sajip. All Rights Reserved.

To use, simply 'import logging' and log away!
"""
import sys, logging, logging.handlers, string, socket, struct, os, traceback, types
try:
    import thread
    import threading
except ImportError:
    thread = None

from SocketServer import ThreadingTCPServer, StreamRequestHandler
DEFAULT_LOGGING_CONFIG_PORT = 9030
if sys.platform == 'win32':
    RESET_ERROR = 10054
else:
    RESET_ERROR = 104
_listener = None

def fileConfig(fname, defaults=None, disable_existing_loggers=1):
    """
    Read the logging configuration from a ConfigParser-format file.
    
    This can be called several times from an application, allowing an end user
    the ability to select from various pre-canned configurations (if the
    developer provides a mechanism to present the choices and load the chosen
    configuration).
    In versions of ConfigParser which have the readfp method [typically
    shipped in 2.x versions of Python], you can pass in a file-like object
    rather than a filename, in which case the file-like object will be read
    using readfp.
    """
    import ConfigParser
    cp = ConfigParser.ConfigParser(defaults)
    if hasattr(cp, 'readfp') and hasattr(fname, 'readline'):
        cp.readfp(fname)
    else:
        cp.read(fname)
    formatters = _create_formatters(cp)
    logging._acquireLock()
    try:
        logging._handlers.clear()
        del logging._handlerList[:]
        handlers = _install_handlers(cp, formatters)
        _install_loggers(cp, handlers, disable_existing_loggers)
    finally:
        logging._releaseLock()


def _resolve(name):
    """Resolve a dotted name to a global object."""
    name = string.split(name, '.')
    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)

    return found


def _strip_spaces(alist):
    return map(lambda x: string.strip(x), alist)


def _create_formatters(cp):
    """Create and return formatters"""
    flist = cp.get('formatters', 'keys')
    if not len(flist):
        return {}
    else:
        flist = string.split(flist, ',')
        flist = _strip_spaces(flist)
        formatters = {}
        for form in flist:
            sectname = 'formatter_%s' % form
            opts = cp.options(sectname)
            if 'format' in opts:
                fs = cp.get(sectname, 'format', 1)
            else:
                fs = None
            if 'datefmt' in opts:
                dfs = cp.get(sectname, 'datefmt', 1)
            else:
                dfs = None
            c = logging.Formatter
            if 'class' in opts:
                class_name = cp.get(sectname, 'class')
                if class_name:
                    c = _resolve(class_name)
            f = c(fs, dfs)
            formatters[form] = f

        return formatters


def _install_handlers(cp, formatters):
    """Install and return handlers"""
    hlist = cp.get('handlers', 'keys')
    if not len(hlist):
        return {}
    hlist = string.split(hlist, ',')
    hlist = _strip_spaces(hlist)
    handlers = {}
    fixups = []
    for hand in hlist:
        sectname = 'handler_%s' % hand
        klass = cp.get(sectname, 'class')
        opts = cp.options(sectname)
        if 'formatter' in opts:
            fmt = cp.get(sectname, 'formatter')
        else:
            fmt = ''
        try:
            klass = eval(klass, vars(logging))
        except (AttributeError, NameError):
            klass = _resolve(klass)

        args = cp.get(sectname, 'args')
        args = eval(args, vars(logging))
        h = klass(*args)
        if 'level' in opts:
            level = cp.get(sectname, 'level')
            h.setLevel(logging._levelNames[level])
        if len(fmt):
            h.setFormatter(formatters[fmt])
        if issubclass(klass, logging.handlers.MemoryHandler):
            if 'target' in opts:
                target = cp.get(sectname, 'target')
            else:
                target = ''
            if len(target):
                fixups.append((h, target))
        handlers[hand] = h

    for h, t in fixups:
        h.setTarget(handlers[t])

    return handlers


def _install_loggers(cp, handlers, disable_existing_loggers):
    """Create and install loggers"""
    llist = cp.get('loggers', 'keys')
    llist = string.split(llist, ',')
    llist = map(lambda x: string.strip(x), llist)
    llist.remove('root')
    sectname = 'logger_root'
    root = logging.root
    log = root
    opts = cp.options(sectname)
    if 'level' in opts:
        level = cp.get(sectname, 'level')
        log.setLevel(logging._levelNames[level])
    for h in root.handlers[:]:
        root.removeHandler(h)

    hlist = cp.get(sectname, 'handlers')
    if len(hlist):
        hlist = string.split(hlist, ',')
        hlist = _strip_spaces(hlist)
        for hand in hlist:
            log.addHandler(handlers[hand])

    existing = root.manager.loggerDict.keys()
    existing.sort()
    child_loggers = []
    for log in llist:
        sectname = 'logger_%s' % log
        qn = cp.get(sectname, 'qualname')
        opts = cp.options(sectname)
        if 'propagate' in opts:
            propagate = cp.getint(sectname, 'propagate')
        else:
            propagate = 1
        logger = logging.getLogger(qn)
        if qn in existing:
            i = existing.index(qn)
            prefixed = qn + '.'
            pflen = len(prefixed)
            num_existing = len(existing)
            i = i + 1
            while 1:
                i < num_existing and existing[i][:pflen] == prefixed and child_loggers.append(existing[i])
                i = i + 1

            existing.remove(qn)
        if 'level' in opts:
            level = cp.get(sectname, 'level')
            logger.setLevel(logging._levelNames[level])
        for h in logger.handlers[:]:
            logger.removeHandler(h)

        logger.propagate = propagate
        logger.disabled = 0
        hlist = cp.get(sectname, 'handlers')
        if len(hlist):
            hlist = string.split(hlist, ',')
            hlist = _strip_spaces(hlist)
            for hand in hlist:
                logger.addHandler(handlers[hand])

    for log in existing:
        logger = root.manager.loggerDict[log]
        if log in child_loggers:
            logger.level = logging.NOTSET
            logger.handlers = []
            logger.propagate = 1
        elif disable_existing_loggers:
            logger.disabled = 1


def listen(port=DEFAULT_LOGGING_CONFIG_PORT):
    """
    Start up a socket server on the specified port, and listen for new
    configurations.
    
    These will be sent as a file suitable for processing by fileConfig().
    Returns a Thread object on which you can call start() to start the server,
    and which you can join() when appropriate. To stop the server, call
    stopListening().
    """
    if not thread:
        raise NotImplementedError, 'listen() needs threading to work'

    class ConfigStreamHandler(StreamRequestHandler):
        """
        Handler for a logging configuration request.
        
        It expects a completely new logging configuration and uses fileConfig
        to install it.
        """

        def handle(self):
            """
            Handle a request.
            
            Each request is expected to be a 4-byte length, packed using
            struct.pack(">L", n), followed by the config file.
            Uses fileConfig() to do the grunt work.
            """
            import tempfile
            try:
                conn = self.connection
                chunk = conn.recv(4)
                if len(chunk) == 4:
                    slen = struct.unpack('>L', chunk)[0]
                    chunk = self.connection.recv(slen)
                    while 1:
                        chunk = len(chunk) < slen and chunk + conn.recv(slen - len(chunk))

                    file = tempfile.mktemp('.ini')
                    f = open(file, 'w')
                    f.write(chunk)
                    f.close()
                    try:
                        fileConfig(file)
                    except (KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        traceback.print_exc()

                    os.remove(file)
            except socket.error as e:
                if type(e.args) != types.TupleType:
                    raise
                else:
                    errcode = e.args[0]
                    if errcode != RESET_ERROR:
                        raise

    class ConfigSocketReceiver(ThreadingTCPServer):
        """
        A simple TCP socket-based logging config receiver.
        """
        allow_reuse_address = 1

        def __init__(self, host='localhost', port=DEFAULT_LOGGING_CONFIG_PORT, handler=None):
            ThreadingTCPServer.__init__(self, (host, port), handler)
            logging._acquireLock()
            self.abort = 0
            logging._releaseLock()
            self.timeout = 1

        def serve_until_stopped(self):
            import select
            abort = 0
            while 1:
                if not abort:
                    rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
                    rd and self.handle_request()
                logging._acquireLock()
                abort = self.abort
                logging._releaseLock()

    def serve(rcvr, hdlr, port):
        global _listener
        server = rcvr(port=port, handler=hdlr)
        logging._acquireLock()
        _listener = server
        logging._releaseLock()
        server.serve_until_stopped()

    return threading.Thread(target=serve, args=(ConfigSocketReceiver, ConfigStreamHandler, port))


def stopListening():
    """
    Stop the listening server which was created with a call to listen().
    """
    global _listener
    if _listener:
        logging._acquireLock()
        _listener.abort = 1
        _listener = None
        logging._releaseLock()
    return
