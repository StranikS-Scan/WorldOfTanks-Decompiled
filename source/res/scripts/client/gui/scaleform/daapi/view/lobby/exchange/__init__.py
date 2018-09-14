# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/__init__.py
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.exchange.ConfirmExchangeDialog import ConfirmExchangeDialog
    from gui.Scaleform.daapi.view.lobby.exchange.ExchangeWindow import ExchangeWindow
    from gui.Scaleform.daapi.view.lobby.exchange.ExchangeXPWindow import ExchangeXPWindow
    from gui.Scaleform.daapi.view.lobby.exchange.ExchangeFreeToTankmanXpWindow import ExchangeFreeToTankmanXpWindow
    return (GroupedViewSettings(VIEW_ALIAS.CONFIRM_EXCHANGE_DIALOG, ConfirmExchangeDialog, 'confirmExchangeDialog.swf', ViewTypes.WINDOW, 'confirmExchangeDialog', None, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.EXCHANGE_WINDOW, ExchangeWindow, 'exchangeWindow.swf', ViewTypes.WINDOW, 'exchangeWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.EXCHANGE_XP_WINDOW, ExchangeXPWindow, 'exchangeXPWindow.swf', ViewTypes.WINDOW, 'exchangeXPWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, ExchangeFreeToTankmanXpWindow, 'exchangeFreeToTankmanXpWindow.swf', ViewTypes.WINDOW, 'exchangeFreeToTankmanXpWindow', None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_ExchangeDialogBusinessHandler(), _ExchangeViewsBusinessHandler())


class _ExchangeDialogBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((ShowDialogEvent.SHOW_EXCHANGE_DIALOG, self.__exchangeDialogHandler),)
        super(_ExchangeDialogBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.DEFAULT)

    def __exchangeDialogHandler(self, event):
        name = 'exchange' + event.meta.getType()
        self.__loadOrUpdateDialog(name, VIEW_ALIAS.CONFIRM_EXCHANGE_DIALOG, event.meta, event.handler)

    def __loadOrUpdateDialog(self, name, alias, meta, handler):
        window = self.findViewByName(ViewTypes.WINDOW, name)
        if window is not None:
            window.updateDialog(meta, handler)
            self.bringViewToFront(name)
        else:
            self.loadViewWithDefName(alias, name, meta, handler)
        return


class _ExchangeViewsBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.EXCHANGE_WINDOW, self.loadViewByCtxEvent), (VIEW_ALIAS.EXCHANGE_XP_WINDOW, self.loadViewByCtxEvent), (VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, self.loadViewByCtxEvent))
        super(_ExchangeViewsBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
