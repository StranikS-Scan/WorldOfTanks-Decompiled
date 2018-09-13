# Embedded file name: scripts/client/messenger/proto/xmpp/logger.py
from collections import deque, defaultdict
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler, ClientHolder
from messenger.proto.xmpp.gloox_wrapper import LOG_LEVEL, LOG_SOURCE
from messenger.proto.xmpp.gloox_wrapper import GLOOX_EVENT, SUBSCRIPTION
from messenger.storage import dyn_storage_getter

class _IEventLogger(object):

    def log(self, level, source, message):
        pass

    def clear(self):
        pass


class _IInternalLogger(object):

    def log(self):
        pass

    def clear(self):
        pass


class _XMPPStreamLogger(_IEventLogger):

    def __init__(self):
        super(_XMPPStreamLogger, self).__init__()
        self.__stream = deque([], 500)

    def log(self, level, source, message):
        if source in LOG_SOURCE.XML_STREAM:
            self.__stream.append((source, message))

    def clear(self):
        self.__stream.clear()

    def tail(self):
        return self.__stream[-1]

    def all(self, request = None):
        result = ['XMPPClient::XML. Prints stream to log:']
        for source, message in self.__stream:
            if request is None or source == request:
                result.append(message)

        LOG_DEBUG('\n'.join(result))
        return

    def flush(self):
        self.all()
        self.clear()


class _OutStreamLogger(_IEventLogger):

    def __init__(self):
        super(_OutStreamLogger, self).__init__()
        self._printers = {LOG_LEVEL.DEBUG: LOG_DEBUG,
         LOG_LEVEL.WARNING: LOG_WARNING,
         LOG_LEVEL.ERROR: LOG_ERROR}

    def log(self, level, source, message):
        if source not in LOG_SOURCE.XML_STREAM:
            if level in self._printers:
                printer = self._printers[level]
            else:
                printer = LOG_DEBUG
            printer('XMPPClient::{0}'.format(source), message)


class _RosterLogger(_IInternalLogger, ClientHolder):

    @dyn_storage_getter('xmppRoster')
    def xmppRoster(self):
        return None

    def log(self, request = None):
        if g_settings.server.XMPP.isEnabled():
            client = self.client()
            if client and client.isConnected():
                roster = self.xmppRoster
                result = ['XMPPClient::RosterItemsLog, Client is connected to XMPP. XMPP roster is:']
                for jid, item in roster.iteritems():
                    if request is None or request == 'to' and item.subscriptionTo != SUBSCRIPTION.OFF or request == 'from' and item.subscriptionFrom != SUBSCRIPTION.OFF:
                        result.append(repr(item))

                LOG_DEBUG('\n'.join(result))
            else:
                LOG_DEBUG('XMPPClient::RosterItemsLog, client is not connected to XMPP yet. Try to run it command later.')
        else:
            LOG_DEBUG('XMPPClient::RosterItemsLog, XMPP protocol is disabled.')
        return


class _GroupsLogger(_IInternalLogger, ClientHolder):

    @dyn_storage_getter('xmppRoster')
    def xmppRoster(self):
        return None

    def log(self):
        if g_settings.server.XMPP.isEnabled():
            client = self.client()
            if client and client.isConnected():
                roster = self.xmppRoster
                result = ['XMPPClient::GroupLog, Client is connected to XMPP. XMPP groups are:']
                groups = defaultdict(set)
                for item in roster.itervalues():
                    if len(item.groups):
                        contactGroups = item.groups
                        for group in contactGroups:
                            groups[group].add('name = {0}, jid = {1}'.format(item.name, item.jid))

                for group, names in sorted(groups.iteritems()):
                    result.append(group + ':')
                    result.append('\t\t' + '\n\t\t'.join(names))
                    result.append('\n')

                LOG_DEBUG('\n'.join(result))
            else:
                LOG_DEBUG('XMPPClient::GroupLog, client is not connected to XMPP yet. Try to run it command later.')
        else:
            LOG_DEBUG('XMPPClient::GroupLog, XMPP protocol is disabled.')


class _SettingsLogger(_IInternalLogger):

    def log(self):
        LOG_DEBUG('XMPPClient::Settings', g_settings.server.XMPP)
        LOG_DEBUG('XMPPClient::UseToShowOnline', g_settings.server.useToShowOnline(PROTO_TYPE.XMPP))


class _ConnectionLogger(_IInternalLogger, ClientHolder):

    def log(self):
        if g_settings.server.XMPP.isEnabled():
            client = self.client()
            if client and client.isConnected():
                LOG_DEBUG('XMPPClient::ConnectionLog, client is connected to XMPP', client.getConnectionAddress())
            else:
                LOG_DEBUG('XMPPClient::ConnectionLog, client is not connected to XMPP')
        else:
            LOG_DEBUG('XMPPClient::ConnectionLog, XMPP protocol is disabled.')


class LogHandler(ClientEventsHandler):

    def __init__(self):
        super(LogHandler, self).__init__()
        self.__eventsLoggers = {'out': _OutStreamLogger()}
        self.__internalLoggers = {'roster': _RosterLogger(),
         'groups': _GroupsLogger(),
         'settings': _SettingsLogger(),
         'connection': _ConnectionLogger()}
        if IS_DEVELOPMENT:
            self.__eventsLoggers['xml'] = _XMPPStreamLogger()

    def event(self, key):
        if key in self.__eventsLoggers:
            return self.__eventsLoggers[key]
        LOG_ERROR('XMPPClient::Log, events logger is not found. Available loggers are', self.__eventsLoggers.keys())

    def internal(self, key):
        if key in self.__internalLoggers:
            return self.__internalLoggers[key]
        LOG_ERROR('XMPPClient::Log, internal logger is not found. Available loggers are', self.__internalLoggers.keys())

    def clear(self):
        for logger in self.__eventsLoggers.itervalues():
            logger.clear()

        for logger in self.__internalLoggers.itervalues():
            logger.clear()

    def registerHandlers(self):
        self.client().registerHandler(GLOOX_EVENT.LOG, self.__handleLog)

    def unregisterHandlers(self):
        self.client().unregisterHandler(GLOOX_EVENT.LOG, self.__handleLog)

    def __handleLog(self, level, source, message):
        for logger in self.__eventsLoggers.itervalues():
            logger.log(level, source, message)

    def __repr__(self):
        return 'LogHandler(id=0x{0:08X}, event({1!r:s}), internal({2!r:s}))'.format(id(self), self.__eventsLoggers.keys(), self.__internalLoggers.keys())
