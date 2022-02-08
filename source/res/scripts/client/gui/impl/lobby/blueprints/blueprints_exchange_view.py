# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/blueprints/blueprints_exchange_view.py
from functools import partial
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebViewTransparent
from gui.shared.event_dispatcher import showBlueprintsSalePage, showHangar
from web.web_client_api.ui import OpenTabWebApi

class _OpenTabWebApi(OpenTabWebApi):

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.BLUEPRINTS_EXCHANGE_VIEW

    def _getVehiclePreviewReturnCallback(self, cmd):
        self.__getBackCallback(cmd)

    def _getVehicleStylePreviewCallback(self, cmd):
        self.__getBackCallback(cmd)

    def __getBackCallback(self, cmd):
        return partial(self.__goBack, cmd.back_url)

    def __goBack(self, url):
        showHangar()
        showBlueprintsSalePage(url)


class BlueprintsExchangeView(WebViewTransparent):

    def __init__(self, ctx=None):
        ctx = ctx or {}
        ctx['allowRightClick'] = False
        super(BlueprintsExchangeView, self).__init__(ctx)

    @property
    def webHandlersReplacements(self):
        return {'open_tab': _OpenTabWebApi}
