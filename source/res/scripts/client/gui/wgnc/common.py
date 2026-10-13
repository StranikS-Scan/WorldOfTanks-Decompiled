# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/common.py
import logging
import typing
if typing.TYPE_CHECKING:
    from web.web_client_api import CommandHandler
_logger = logging.getLogger(__name__)

class WebHandlersContainer(object):
    _webHandlers = {}

    @classmethod
    def addWebHandler(cls, name, handler):
        cls._webHandlers[name] = handler

    @classmethod
    def removeWebHandler(cls, name):
        if name in cls._webHandlers:
            del cls._webHandlers[name]

    @classmethod
    def getWebHandler(cls, name):
        if name is None:
            return
        elif name not in cls._webHandlers:
            _logger.warning("Cannot get web client handler by name '%s'", name)
            return
        else:
            return cls._webHandlers[name]
