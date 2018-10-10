# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/logging/config.py
import cStringIO
import errno
import io
import logging
import logging.handlers
import os
import re
import socket
import struct
import sys
import traceback
import types
try:
    import thread
    import threading
except ImportError:
    thread = None

from SocketServer import ThreadingTCPServer, StreamRequestHandler
DEFAULT_LOGGING_CONFIG_PORT = 9030
RESET_ERROR = errno.ECONNRESET
_listener = None

def fileConfig(fname, defaults=None, disable_existing_loggers=True):
    import ConfigParser
    cp = ConfigParser.ConfigParser(defaults)
    if hasattr(fname, 'readline'):
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
    name = name.split('.')
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
    return map(lambda x: x.strip(), alist)


def _encoded(s):
    return s if isinstance(s, str) else s.encode('utf-8')


def _create_formatters(cp):
    flist = cp.get('formatters', 'keys')
    if not len(flist):
        return {}
    else:
        flist = flist.split(',')
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
    hlist = cp.get('handlers', 'keys')
    if not len(hlist):
        return {}
    hlist = hlist.split(',')
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
    llist = cp.get('loggers', 'keys')
    llist = llist.split(',')
    llist = list(map(lambda x: x.strip(), llist))
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
        hlist = hlist.split(',')
        hlist = _strip_spaces(hlist)
        for hand in hlist:
            log.addHandler(handlers[hand])

    existing = list(root.manager.loggerDict.keys())
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
            i = existing.index(qn) + 1
            prefixed = qn + '.'
            pflen = len(prefixed)
            num_existing = len(existing)
            while i < num_existing:
                if existing[i][:pflen] == prefixed:
                    child_loggers.append(existing[i])
                i += 1

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
            hlist = hlist.split(',')
            hlist = _strip_spaces(hlist)
            for hand in hlist:
                logger.addHandler(handlers[hand])

    for log in existing:
        logger = root.manager.loggerDict[log]
        if log in child_loggers:
            logger.level = logging.NOTSET
            logger.handlers = []
            logger.propagate = 1
        logger.disabled = disable_existing_loggers


IDENTIFIER = re.compile('^[a-z_][a-z0-9_]*$', re.I)

def valid_ident(s):
    m = IDENTIFIER.match(s)
    if not m:
        raise ValueError('Not a valid Python identifier: %r' % s)
    return True


class ConvertingMixin(object):

    def convert_with_key(self, key, value, replace=True):
        result = self.configurator.convert(value)
        if value is not result:
            if replace:
                self[key] = result
            if type(result) in (ConvertingDict, ConvertingList, ConvertingTuple):
                result.parent = self
                result.key = key
        return result

    def convert(self, value):
        result = self.configurator.convert(value)
        if value is not result:
            if type(result) in (ConvertingDict, ConvertingList, ConvertingTuple):
                result.parent = self
        return result


class ConvertingDict(dict, ConvertingMixin):

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        return self.convert_with_key(key, value)

    def get(self, key, default=None):
        value = dict.get(self, key, default)
        return self.convert_with_key(key, value)

    def pop(self, key, default=None):
        value = dict.pop(self, key, default)
        return self.convert_with_key(key, value, replace=False)


class ConvertingList(list, ConvertingMixin):

    def __getitem__(self, key):
        value = list.__getitem__(self, key)
        return self.convert_with_key(key, value)

    def pop(self, idx=-1):
        value = list.pop(self, idx)
        return self.convert(value)


class ConvertingTuple(tuple, ConvertingMixin):

    def __getitem__(self, key):
        value = tuple.__getitem__(self, key)
        return self.convert_with_key(key, value, replace=False)


class BaseConfigurator(object):
    CONVERT_PATTERN = re.compile('^(?P<prefix>[a-z]+)://(?P<suffix>.*)$')
    WORD_PATTERN = re.compile('^\\s*(\\w+)\\s*')
    DOT_PATTERN = re.compile('^\\.\\s*(\\w+)\\s*')
    INDEX_PATTERN = re.compile('^\\[\\s*(\\w+)\\s*\\]\\s*')
    DIGIT_PATTERN = re.compile('^\\d+$')
    value_converters = {'ext': 'ext_convert',
     'cfg': 'cfg_convert'}
    importer = __import__

    def __init__(self, config):
        self.config = ConvertingDict(config)
        self.config.configurator = self
        if type(__import__) == types.FunctionType:
            self.importer = __import__

    def resolve(self, s):
        name = s.split('.')
        used = name.pop(0)
        try:
            found = self.importer(used)
            for frag in name:
                used += '.' + frag
                try:
                    found = getattr(found, frag)
                except AttributeError:
                    self.importer(used)
                    found = getattr(found, frag)

            return found
        except ImportError:
            e, tb = sys.exc_info()[1:]
            v = ValueError('Cannot resolve %r: %s' % (s, e))
            v.__cause__, v.__traceback__ = e, tb
            raise v

    def ext_convert(self, value):
        return self.resolve(value)

    def cfg_convert(self, value):
        rest = value
        m = self.WORD_PATTERN.match(rest)
        if m is None:
            raise ValueError('Unable to convert %r' % value)
        else:
            rest = rest[m.end():]
            d = self.config[m.groups()[0]]
            while rest:
                m = self.DOT_PATTERN.match(rest)
                if m:
                    d = d[m.groups()[0]]
                else:
                    m = self.INDEX_PATTERN.match(rest)
                    if m:
                        idx = m.groups()[0]
                        if not self.DIGIT_PATTERN.match(idx):
                            d = d[idx]
                        else:
                            try:
                                n = int(idx)
                                d = d[n]
                            except TypeError:
                                d = d[idx]

                if m:
                    rest = rest[m.end():]
                raise ValueError('Unable to convert %r at %r' % (value, rest))

        return d

    def convert(self, value):
        if not isinstance(value, ConvertingDict) and isinstance(value, dict):
            value = ConvertingDict(value)
            value.configurator = self
        elif not isinstance(value, ConvertingList) and isinstance(value, list):
            value = ConvertingList(value)
            value.configurator = self
        elif not isinstance(value, ConvertingTuple) and isinstance(value, tuple):
            value = ConvertingTuple(value)
            value.configurator = self
        elif isinstance(value, basestring):
            m = self.CONVERT_PATTERN.match(value)
            if m:
                d = m.groupdict()
                prefix = d['prefix']
                converter = self.value_converters.get(prefix, None)
                if converter:
                    suffix = d['suffix']
                    converter = getattr(self, converter)
                    value = converter(suffix)
        return value

    def configure_custom(self, config):
        c = config.pop('()')
        if not hasattr(c, '__call__') and hasattr(types, 'ClassType') and type(c) != types.ClassType:
            c = self.resolve(c)
        props = config.pop('.', None)
        kwargs = dict([ (k, config[k]) for k in config if valid_ident(k) ])
        result = c(**kwargs)
        if props:
            for name, value in props.items():
                setattr(result, name, value)

        return result

    def as_tuple(self, value):
        if isinstance(value, list):
            value = tuple(value)
        return value


class DictConfigurator(BaseConfigurator):

    def configure(self):
        config = self.config
        if 'version' not in config:
            raise ValueError("dictionary doesn't specify a version")
        if config['version'] != 1:
            raise ValueError('Unsupported version: %s' % config['version'])
        incremental = config.pop('incremental', False)
        EMPTY_DICT = {}
        logging._acquireLock()
        try:
            if incremental:
                handlers = config.get('handlers', EMPTY_DICT)
                for name in handlers:
                    if name not in logging._handlers:
                        raise ValueError('No handler found with name %r' % name)
                    try:
                        handler = logging._handlers[name]
                        handler_config = handlers[name]
                        level = handler_config.get('level', None)
                        if level:
                            handler.setLevel(logging._checkLevel(level))
                    except StandardError as e:
                        raise ValueError('Unable to configure handler %r: %s' % (name, e))

                loggers = config.get('loggers', EMPTY_DICT)
                for name in loggers:
                    try:
                        self.configure_logger(name, loggers[name], True)
                    except StandardError as e:
                        raise ValueError('Unable to configure logger %r: %s' % (name, e))

                root = config.get('root', None)
                if root:
                    try:
                        self.configure_root(root, True)
                    except StandardError as e:
                        raise ValueError('Unable to configure root logger: %s' % e)

            else:
                disable_existing = config.pop('disable_existing_loggers', True)
                logging._handlers.clear()
                del logging._handlerList[:]
                formatters = config.get('formatters', EMPTY_DICT)
                for name in formatters:
                    try:
                        formatters[name] = self.configure_formatter(formatters[name])
                    except StandardError as e:
                        raise ValueError('Unable to configure formatter %r: %s' % (name, e))

                filters = config.get('filters', EMPTY_DICT)
                for name in filters:
                    try:
                        filters[name] = self.configure_filter(filters[name])
                    except StandardError as e:
                        raise ValueError('Unable to configure filter %r: %s' % (name, e))

                handlers = config.get('handlers', EMPTY_DICT)
                deferred = []
                for name in sorted(handlers):
                    try:
                        handler = self.configure_handler(handlers[name])
                        handler.name = name
                        handlers[name] = handler
                    except StandardError as e:
                        if 'target not configured yet' in str(e):
                            deferred.append(name)
                        else:
                            raise ValueError('Unable to configure handler %r: %s' % (name, e))

                for name in deferred:
                    try:
                        handler = self.configure_handler(handlers[name])
                        handler.name = name
                        handlers[name] = handler
                    except StandardError as e:
                        raise ValueError('Unable to configure handler %r: %s' % (name, e))

                root = logging.root
                existing = root.manager.loggerDict.keys()
                existing.sort()
                child_loggers = []
                loggers = config.get('loggers', EMPTY_DICT)
                for name in loggers:
                    name = _encoded(name)
                    if name in existing:
                        i = existing.index(name)
                        prefixed = name + '.'
                        pflen = len(prefixed)
                        num_existing = len(existing)
                        i = i + 1
                        while 1:
                            i < num_existing and existing[i][:pflen] == prefixed and child_loggers.append(existing[i])
                            i = i + 1

                        existing.remove(name)
                    try:
                        self.configure_logger(name, loggers[name])
                    except StandardError as e:
                        raise ValueError('Unable to configure logger %r: %s' % (name, e))

                for log in existing:
                    logger = root.manager.loggerDict[log]
                    if log in child_loggers:
                        logger.level = logging.NOTSET
                        logger.handlers = []
                        logger.propagate = True
                    if disable_existing:
                        logger.disabled = True

                root = config.get('root', None)
                if root:
                    try:
                        self.configure_root(root)
                    except StandardError as e:
                        raise ValueError('Unable to configure root logger: %s' % e)

        finally:
            logging._releaseLock()

        return

    def configure_formatter(self, config):
        if '()' in config:
            factory = config['()']
            try:
                result = self.configure_custom(config)
            except TypeError as te:
                if "'format'" not in str(te):
                    raise
                config['fmt'] = config.pop('format')
                config['()'] = factory
                result = self.configure_custom(config)

        else:
            fmt = config.get('format', None)
            dfmt = config.get('datefmt', None)
            result = logging.Formatter(fmt, dfmt)
        return result

    def configure_filter(self, config):
        if '()' in config:
            result = self.configure_custom(config)
        else:
            name = config.get('name', '')
            result = logging.Filter(name)
        return result

    def add_filters(self, filterer, filters):
        for f in filters:
            try:
                filterer.addFilter(self.config['filters'][f])
            except StandardError as e:
                raise ValueError('Unable to add filter %r: %s' % (f, e))

    def configure_handler(self, config):
        formatter = config.pop('formatter', None)
        if formatter:
            try:
                formatter = self.config['formatters'][formatter]
            except StandardError as e:
                raise ValueError('Unable to set formatter %r: %s' % (formatter, e))

        level = config.pop('level', None)
        filters = config.pop('filters', None)
        if '()' in config:
            c = config.pop('()')
            if not hasattr(c, '__call__') and hasattr(types, 'ClassType') and type(c) != types.ClassType:
                c = self.resolve(c)
            factory = c
        else:
            cname = config.pop('class')
            klass = self.resolve(cname)
            if issubclass(klass, logging.handlers.MemoryHandler) and 'target' in config:
                try:
                    th = self.config['handlers'][config['target']]
                    if not isinstance(th, logging.Handler):
                        config['class'] = cname
                        raise StandardError('target not configured yet')
                    config['target'] = th
                except StandardError as e:
                    raise ValueError('Unable to set target handler %r: %s' % (config['target'], e))

            elif issubclass(klass, logging.handlers.SMTPHandler) and 'mailhost' in config:
                config['mailhost'] = self.as_tuple(config['mailhost'])
            elif issubclass(klass, logging.handlers.SysLogHandler) and 'address' in config:
                config['address'] = self.as_tuple(config['address'])
            factory = klass
        kwargs = dict([ (k, config[k]) for k in config if valid_ident(k) ])
        try:
            result = factory(**kwargs)
        except TypeError as te:
            if "'stream'" not in str(te):
                raise
            kwargs['strm'] = kwargs.pop('stream')
            result = factory(**kwargs)

        if formatter:
            result.setFormatter(formatter)
        if level is not None:
            result.setLevel(logging._checkLevel(level))
        if filters:
            self.add_filters(result, filters)
        return result

    def add_handlers(self, logger, handlers):
        for h in handlers:
            try:
                logger.addHandler(self.config['handlers'][h])
            except StandardError as e:
                raise ValueError('Unable to add handler %r: %s' % (h, e))

    def common_logger_config(self, logger, config, incremental=False):
        level = config.get('level', None)
        if level is not None:
            logger.setLevel(logging._checkLevel(level))
        if not incremental:
            for h in logger.handlers[:]:
                logger.removeHandler(h)

            handlers = config.get('handlers', None)
            if handlers:
                self.add_handlers(logger, handlers)
            filters = config.get('filters', None)
            if filters:
                self.add_filters(logger, filters)
        return

    def configure_logger(self, name, config, incremental=False):
        logger = logging.getLogger(name)
        self.common_logger_config(logger, config, incremental)
        propagate = config.get('propagate', None)
        if propagate is not None:
            logger.propagate = propagate
        return

    def configure_root(self, config, incremental=False):
        root = logging.getLogger()
        self.common_logger_config(root, config, incremental)


dictConfigClass = DictConfigurator

def dictConfig(config):
    dictConfigClass(config).configure()


def listen(port=DEFAULT_LOGGING_CONFIG_PORT):
    if not thread:
        raise NotImplementedError('listen() needs threading to work')

    class ConfigStreamHandler(StreamRequestHandler):

        def handle(self):
            import tempfile
            try:
                conn = self.connection
                chunk = conn.recv(4)
                if len(chunk) == 4:
                    slen = struct.unpack('>L', chunk)[0]
                    chunk = self.connection.recv(slen)
                    while len(chunk) < slen:
                        chunk = chunk + conn.recv(slen - len(chunk))

                    try:
                        import json
                        d = json.loads(chunk)
                        dictConfig(d)
                    except:
                        file = cStringIO.StringIO(chunk)
                        try:
                            fileConfig(file)
                        except (KeyboardInterrupt, SystemExit):
                            raise
                        except:
                            traceback.print_exc()

                    if self.server.ready:
                        self.server.ready.set()
            except socket.error as e:
                if e.errno != RESET_ERROR:
                    raise

    class ConfigSocketReceiver(ThreadingTCPServer):
        allow_reuse_address = 1

        def __init__(self, host='localhost', port=DEFAULT_LOGGING_CONFIG_PORT, handler=None, ready=None):
            ThreadingTCPServer.__init__(self, (host, port), handler)
            logging._acquireLock()
            self.abort = 0
            logging._releaseLock()
            self.timeout = 1
            self.ready = ready

        def serve_until_stopped(self):
            import select
            abort = 0
            while not abort:
                rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
                if rd:
                    self.handle_request()
                logging._acquireLock()
                abort = self.abort
                logging._releaseLock()

            self.socket.close()

    class Server(threading.Thread):

        def __init__(self, rcvr, hdlr, port):
            super(Server, self).__init__()
            self.rcvr = rcvr
            self.hdlr = hdlr
            self.port = port
            self.ready = threading.Event()

        def run(self):
            global _listener
            server = self.rcvr(port=self.port, handler=self.hdlr, ready=self.ready)
            if self.port == 0:
                self.port = server.server_address[1]
            self.ready.set()
            logging._acquireLock()
            _listener = server
            logging._releaseLock()
            server.serve_until_stopped()

    return Server(ConfigSocketReceiver, ConfigStreamHandler, port)


def stopListening():
    global _listener
    logging._acquireLock()
    try:
        if _listener:
            _listener.abort = 1
            _listener = None
    finally:
        logging._releaseLock()

    return
