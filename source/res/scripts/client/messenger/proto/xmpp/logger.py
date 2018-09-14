# Embedded file name: scripts/client/messenger/proto/xmpp/logger.py
from collections import defaultdict
import time
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler, ClientHolder
from messenger.proto.xmpp.gloox_wrapper import LOG_LEVEL, LOG_SOURCE
from messenger.proto.xmpp.gloox_wrapper import GLOOX_EVENT, SUBSCRIPTION
from messenger.proto.xmpp.log_output import CLIENT_LOG_AREA, g_logOutput
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


def _getLogFunction(output, level):
    if level == LOG_LEVEL.ERROR:
        logger = output.error
    elif level == LOG_LEVEL.WARNING:
        logger = output.warning
    else:
        logger = output.debug
    return logger


class _GlooxLogger(_IEventLogger):

    def log(self, level, source, message):
        if source in LOG_SOURCE.XML_STREAM:
            area = CLIENT_LOG_AREA.GLOOX_XML
        else:
            area = CLIENT_LOG_AREA.GLOOX_SOURCE
        logger = _getLogFunction(g_logOutput, level)
        logger(area, source, message)


class _RosterLogger(_IInternalLogger, ClientHolder):

    @dyn_storage_getter('xmppRoster')
    def xmppRoster(self):
        return None

    def log(self, request = None):
        if g_settings.server.XMPP.isEnabled():
            client = self.client()
            if client and client.isConnected():
                roster = self.xmppRoster
                result = ['Client is connected to XMPP. XMPP roster is:']
                for jid, item in roster.iteritems():
                    if request is None or request == 'to' and item.subscriptionTo != SUBSCRIPTION.OFF or request == 'from' and item.subscriptionFrom != SUBSCRIPTION.OFF:
                        result.append(repr(item))

                g_logOutput.debug(CLIENT_LOG_AREA.ROSTER, '\n'.join(result))
            else:
                g_logOutput.debug(CLIENT_LOG_AREA.ROSTER, 'Client is not connected to XMPP yet. Try to run it command later.')
        else:
            g_logOutput.debug(CLIENT_LOG_AREA.ROSTER, 'XMPP protocol is disabled')
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
                result = ['Client is connected to XMPP. XMPP groups are:']
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

                g_logOutput.debug(CLIENT_LOG_AREA.GROUP, '\n'.join(result))
            else:
                g_logOutput.debug(CLIENT_LOG_AREA.GROUP, 'Client is not connected to XMPP yet. Try to run it command later')
        else:
            g_logOutput.debug(CLIENT_LOG_AREA.GROUP, 'XMPP protocol is disabled')


class _SettingsLogger(_IInternalLogger):

    def log(self):
        g_logOutput.debug(CLIENT_LOG_AREA.SETTINGS, 'XMPP settings', g_settings.server.XMPP)
        g_logOutput.debug(CLIENT_LOG_AREA.SETTINGS, 'Uses XMPP to show online', g_settings.server.useToShowOnline(PROTO_TYPE.XMPP))


class _ConnectionLogger(_IInternalLogger, ClientHolder):

    def log(self):
        if g_settings.server.XMPP.isEnabled():
            client = self.client()
            if client and client.isConnected():
                g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'Client is connected to XMPP', client.getConnectionAddress())
            else:
                g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'Client is not connected to XMPP')
        else:
            g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'XMPP protocol is disabled')


class LogHandler(ClientEventsHandler):

    def __init__(self):
        super(LogHandler, self).__init__()
        self.__eventsLoggers = {'out': _GlooxLogger()}
        self.__internalLoggers = {'roster': _RosterLogger(),
         'groups': _GroupsLogger(),
         'settings': _SettingsLogger(),
         'connection': _ConnectionLogger()}

    def event(self, key):
        if key in self.__eventsLoggers:
            return self.__eventsLoggers[key]
        else:
            g_logOutput.error(CLIENT_LOG_AREA.GENERIC, 'Events logger is not found. Available loggers are', self.__eventsLoggers.keys())
            return None
            return None

    def internal(self, key):
        if key in self.__internalLoggers:
            return self.__internalLoggers[key]
        else:
            g_logOutput.error(CLIENT_LOG_AREA.GENERIC, 'Events logger is not found. Available loggers are', self.__internalLoggers.keys())
            return None
            return None

    def getEventNames(self):
        return self.__eventsLoggers.keys()

    def getInternalNames(self):
        return self.__internalLoggers.keys()

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


class XMPP_EVENT_LOG(object):
    DISCONNECT = 1


def sendEventToServer(eventType, host, port, errorCode = 0, errorDescr = '', tries = 1):
    sender = getattr(BigWorld.player(), 'logXMPPEvents', None)
    if not sender or not callable(sender):
        return
    else:
        address = '{0}:{1}'.format(host, port)
        try:
            sender([eventType,
             time.time(),
             errorCode,
             tries], [address, errorDescr])
        except:
            LOG_CURRENT_EXCEPTION()

        return
