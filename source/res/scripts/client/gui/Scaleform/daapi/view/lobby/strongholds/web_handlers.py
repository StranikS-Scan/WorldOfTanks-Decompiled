# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/strongholds/web_handlers.py
from web_client_api import webApiCollection
from web_client_api.clans import ClansWebApi
from web_client_api.strongholds import StrongholdsWebApi
from web_client_api.request import RequestWebApi
from web_client_api.sound import SoundWebApi
from web_client_api.ui import NotificationWebApi, OpenWindowWebApi, OpenTabWebApi, ContextMenuWebApi, CloseWindowWebApi

def createStrongholdsWebHandlers(onBrowserOpen=None, onBrowserClose=None):

    class _OpenWindowWebApi(OpenWindowWebApi):

        def _createHandlers(self):
            return createStrongholdsWebHandlers(onBrowserOpen, onBrowserClose)

        def _onBrowserOpen(self, alias):
            onBrowserOpen(alias)

    class _CloseWindowWebApi(CloseWindowWebApi):

        def _onBrowserClose(self):
            onBrowserClose()

    return webApiCollection(_CloseWindowWebApi, _OpenWindowWebApi, ClansWebApi, ContextMenuWebApi, NotificationWebApi, OpenTabWebApi, RequestWebApi, StrongholdsWebApi, SoundWebApi)
