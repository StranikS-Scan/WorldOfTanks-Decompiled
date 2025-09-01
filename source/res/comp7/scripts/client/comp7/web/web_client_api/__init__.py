# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/web/web_client_api/__init__.py
from comp7.skeletons.gui.game_control import IComp7ShopController
from comp7.web.web_client_api.ui.comp7_ui import OpenComp7Mixin
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from web.web_client_api import w2capi, w2c, W2CSchema
from web.web_client_api.ui import OpenWindowWebApi

@w2capi(name='comp7', key='action')
class Comp7WebApi(OpenComp7Mixin):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __comp7ShopController = dependency.descriptor(IComp7ShopController)

    @w2c(W2CSchema, name='close_browser')
    def closeBrowser(self, _):
        from gui.shared.event_dispatcher import showHangar
        showHangar()

    @w2c(W2CSchema, name='get_gamemode_state')
    def getGamemodeState(self, _):
        return {'isShopEnabled': self.__comp7ShopController.isShopEnabled}


@w2capi(name='open_window', key='window_id')
class Comp7OpenWindowWebApi(OpenWindowWebApi, OpenComp7Mixin):
    pass
