# Embedded file name: scripts/client/messenger/proto/xmpp/log_output.py
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR

class CLIENT_LOG_AREA(object):
    GLOOX_SOURCE, GLOOX_XML, PY_WRAPPER, CONNECTION, LOGIN, TOKEN, ROSTER, GROUP, SETTINGS, GENERIC, SYNC, BLOCK_LIST, RESOURCE, SUBSCRIPTION, MESSAGE = range(15)


CLIENT_LOG_AREA_NAMES = dict([ (v, k) for k, v in CLIENT_LOG_AREA.__dict__.iteritems() if not k.startswith('_') ])

class ILogOutput(object):

    def debug(self, area, message, *args, **kwargs):
        pass

    def warning(self, area, message, *args, **kwargs):
        pass

    def error(self, area, message, *args, **kwargs):
        pass

    def clear(self):
        pass


class ConsoleLogOutput(ILogOutput):

    def debug(self, area, message, *args):
        if area != CLIENT_LOG_AREA.GLOOX_XML:
            LOG_DEBUG(self.__makeHeader(area, message), *args)

    def warning(self, area, message, *args):
        if area != CLIENT_LOG_AREA.GLOOX_XML:
            LOG_WARNING(self.__makeHeader(area, message), *args)

    def error(self, area, message, *args):
        if area != CLIENT_LOG_AREA.GLOOX_XML:
            LOG_ERROR(self.__makeHeader(area, message), *args)

    def __makeHeader(self, area, message):
        if area in CLIENT_LOG_AREA_NAMES:
            name = CLIENT_LOG_AREA_NAMES[area]
        else:
            name = 'N/A'
        return 'XMPP_PY::{0}. {1}'.format(name, message)


class _LogOutputDecorator(ILogOutput):
    __slots__ = ('__outputs',)

    def __init__(self):
        super(_LogOutputDecorator, self).__init__()
        self.__outputs = {'console': ConsoleLogOutput()}

    def addOutput(self, name, output):
        if name not in self.__outputs:
            self.__outputs[name] = output

    def removeOutput(self, name):
        if name in self.__outputs:
            self.__outputs.pop(name)

    def getOutput(self, name):
        output = None
        if name in self.__outputs:
            output = self.__outputs[name]
        return output

    def debug(self, area, message, *args):
        for output in self.__outputs.itervalues():
            output.debug(area, message, *args)

    def warning(self, area, message, *args):
        for output in self.__outputs.itervalues():
            output.warning(area, message, *args)

    def error(self, area, message, *args):
        for output in self.__outputs.itervalues():
            output.error(area, message, *args)

    def clear(self):
        for output in self.__outputs.itervalues():
            output.clear()


g_logOutput = _LogOutputDecorator()
