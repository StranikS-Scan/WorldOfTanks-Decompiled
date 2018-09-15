# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/WebCommandHandler.py
import json
from . import WebCommandException
from commands import WebCommand, instantiateObject, CommandHandler
from debug_utils import LOG_WARNING, LOG_DEBUG
from Event import Event

class WebCommandHandler(object):
    """
    Purpose of this class is to receive json messages from Browser parse them,
    create appropriate commands and handle created commands.
    """

    def __init__(self, browserID, alias, browserView):
        self.__handlers = []
        self.__browserID = browserID
        self.__alias = alias
        self.__browserView = browserView
        self.onCallback = Event()

    def fini(self):
        for handler in self.__handlers:
            finiHandler = handler.finiHandler
            if callable(finiHandler):
                finiHandler()

        self.__handlers = []

    def handleCommand(self, data):
        LOG_DEBUG('Web2Client handle: %s' % data)
        try:
            parsed = json.loads(data, encoding='utf-8')
        except (TypeError, ValueError) as exception:
            raise WebCommandException('Command parse failed! Description: %s' % exception)

        command = instantiateObject(WebCommand, parsed)
        self.handleWebCommand(command)

    def addHandlers(self, handlers):
        for handler in handlers:
            self.addHandler(handler)

    def addHandler(self, handler):
        assert isinstance(handler, CommandHandler)
        if handler not in self.__handlers:
            self.__handlers.append(handler)
        else:
            LOG_WARNING('Handler %s already added to WebCommandHandler!' % str(handler))

    def removeHandler(self, handler):
        if handler in self.__handlers:
            self.__handlers.remove(handler)

    def handleWebCommand(self, webCommand):
        commandName = webCommand.command
        for handler in self.__handlers:
            if commandName == handler.name:
                command = instantiateObject(handler.cls, webCommand.params)
                handler.handler(command, self.__createCtx(commandName, webCommand.web_id))
                return

        raise WebCommandException("Command '%s' is unsupported!" % commandName)

    def __createCtx(self, commandName, webId):

        def callback(data):
            callbackData = {'command': commandName,
             'data': data,
             'web_id': webId}
            LOG_DEBUG('Web2Client callback: %s' % callbackData)
            jsonMessage = json.dumps(callbackData).replace('"', '\\"')
            self.onCallback(jsonMessage)

        return {'browser_id': self.__browserID,
         'browser_alias': self.__alias,
         'browser_view': self.__browserView,
         'callback': callback}
