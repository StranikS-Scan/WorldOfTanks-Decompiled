# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/browser/web_handlers.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showClanQuestWindow
from web.web_client_api import webApiCollection
from web.web_client_api.exchange import PersonalExchangeRatesDiscountsWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import SoundWebApi, SoundStateWebApi
from web.web_client_api.clans import ClansWebApi
from web.web_client_api.strongholds import StrongholdsWebApi
from web.web_client_api.ui import OpenWindowWebApi, OpenTabWebApi, UtilWebApi, ContextMenuWebApi, CloseWindowWebApi

class _OpenTabWebApi(OpenTabWebApi):

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.CLAN_NOTIFICATION_WINDOW

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getReturnCallback(cmd.back_url)

    def __getReturnCallback(self, backUrl):
        return (lambda : showClanQuestWindow(backUrl)) if backUrl is not None else None


def createNotificationWebHandlers():
    return webApiCollection(SoundWebApi, RequestWebApi, ContextMenuWebApi, OpenWindowWebApi, UtilWebApi, RewardsWebApi, SocialWebApi, ShopWebApi, CloseWindowWebApi, _OpenTabWebApi, ClansWebApi, SoundStateWebApi, StrongholdsWebApi, PersonalExchangeRatesDiscountsWebApi)
