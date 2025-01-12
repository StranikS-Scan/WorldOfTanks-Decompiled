# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/comp7/__init__.py
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.game_control import IComp7ShopController, IComp7Controller
from web.web_client_api import w2capi, w2c, W2CSchema
from web.web_client_api.ui.comp7 import OpenComp7Mixin

@w2capi(name='comp7', key='action')
class Comp7WebApi(OpenComp7Mixin):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __comp7ShopController = dependency.descriptor(IComp7ShopController)

    @w2c(W2CSchema, name='close_browser')
    def closeBrowser(self, _):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), EVENT_BUS_SCOPE.LOBBY)

    @w2c(W2CSchema, name='get_gamemode_state')
    def getGamemodeState(self, _):
        return {'isShopEnabled': self.__comp7ShopController.isShopEnabled}
