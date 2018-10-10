# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/web_handlers.py
from gui.shared.event_dispatcher import showWebShop
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from web_client_api import webApiCollection
from web_client_api.request import RequestWebApi
from web_client_api.sound import SoundWebApi
from web_client_api.shop import ShopWebApi
from web_client_api.ui import NotificationWebApi, OpenWindowWebApi, OpenTabWebApi, CloseWindowWebApi, UtilWebApi

class _OpenTabWebApi(OpenTabWebApi):

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.LOBBY_STORE

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getReturnCallback(cmd.back_url)

    def __getReturnCallback(self, backUrl):
        return (lambda : showWebShop(backUrl)) if backUrl is not None else None


def createShopWebHandlers():
    return webApiCollection(CloseWindowWebApi, OpenWindowWebApi, NotificationWebApi, _OpenTabWebApi, RequestWebApi, ShopWebApi, SoundWebApi, UtilWebApi)
