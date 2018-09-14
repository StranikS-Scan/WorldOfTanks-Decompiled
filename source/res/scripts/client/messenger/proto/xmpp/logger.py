# Embedded file name: scripts/client/messenger/proto/xmpp/logger.py
import time
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from messenger.proto.xmpp.gloox_constants import LOG_LEVEL, LOG_SOURCE, GLOOX_EVENT
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler
from messenger.proto.xmpp.log_output import CLIENT_LOG_AREA, g_logOutput

class _IEventLogger(object):

    def log(self, level, source, message):
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


class LogHandler(ClientEventsHandler):

    def __init__(self):
        super(LogHandler, self).__init__()
        self.__loggers = {'out': _GlooxLogger()}

    def logger(self, key):
        if key in self.__loggers:
            return self.__loggers[key]
        else:
            g_logOutput.error(CLIENT_LOG_AREA.GENERIC, 'Events logger is not found. Available loggers are', self.__loggers.keys())
            return None
            return None

    def getNames(self):
        return self.__loggers.keys()

    def clear(self):
        for logger in self.__loggers.itervalues():
            logger.clear()

    def registerHandlers(self):
        self.client().registerHandler(GLOOX_EVENT.LOG, self.__handleLog)

    def unregisterHandlers(self):
        self.client().unregisterHandler(GLOOX_EVENT.LOG, self.__handleLog)

    def __handleLog(self, level, source, message):
        for logger in self.__loggers.itervalues():
            logger.log(level, source, message)

    def __repr__(self):
        return 'LogHandler(id=0x{0:08X}, loggers({1!r:s}))'.format(id(self), self.__loggers.keys())


class XMPP_EVENT_LOG(object):
    DISCONNECT = 1


def sendEventToServer(eventType, host, port, errorCode = 0, errorDescr = '', tries = 1):
    player = BigWorld.player()
    sender = getattr(player, 'logXMPPEvents', None)
    if not sender or not callable(sender) or not player.isPlayer:
        return
    else:
        address = '{0}:{1}'.format(host, port)
        currentTime = time.time()
        g_logOutput.debug(CLIENT_LOG_AREA.GENERIC, 'Sends log to server', [eventType,
         currentTime,
         errorCode,
         tries], [address, errorDescr])
        try:
            sender([eventType,
             currentTime,
             errorCode,
             tries], [address, errorDescr])
        except:
            LOG_CURRENT_EXCEPTION()

        return
