# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.exchange.ConfirmExchangeDialog import ConfirmExchangeDialog
    from gui.Scaleform.daapi.view.lobby.exchange.ExchangeWindow import ExchangeWindow
    from gui.Scaleform.daapi.view.lobby.exchange.ExchangeXPWindow import ExchangeXPWindow
    from gui.Scaleform.daapi.view.lobby.exchange.detailed_exchange_xp_dialog import ExchangeXPWindowDialog
    return (GroupedViewSettings(VIEW_ALIAS.CONFIRM_EXCHANGE_DIALOG, ConfirmExchangeDialog, 'confirmExchangeDialog.swf', WindowLayer.WINDOW, 'confirmExchangeDialog', None, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CONFIRM_EXCHANGE_DIALOG_MODAL, ConfirmExchangeDialog, 'confirmExchangeDialog.swf', WindowLayer.TOP_WINDOW, 'confirmExchangeDialog', None, ScopeTemplates.LOBBY_SUB_SCOPE, isModal=True),
     GroupedViewSettings(VIEW_ALIAS.EXCHANGE_WINDOW, ExchangeWindow, 'exchangeWindow.swf', WindowLayer.WINDOW, 'exchangeWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.EXCHANGE_WINDOW_MODAL, ExchangeWindow, 'exchangeWindow.swf', WindowLayer.TOP_WINDOW, 'exchangeWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.EXCHANGE_XP_WINDOW, ExchangeXPWindow, 'exchangeXPWindow.swf', WindowLayer.WINDOW, 'exchangeXPWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.EXCHANGE_XP_WINDOW_DIALOG_MODAL, ExchangeXPWindowDialog, 'exchangeXPWindow.swf', WindowLayer.TOP_WINDOW, 'exchangeXPWindow', None, ScopeTemplates.LOBBY_SUB_SCOPE, isModal=True),
     GroupedViewSettings(VIEW_ALIAS.CONFIRM_EXCHANGE_BERTHS_DIALOG, ConfirmExchangeDialog, 'confirmExchangeDialog.swf', WindowLayer.FULLSCREEN_WINDOW, 'confirmExchangeDialog', None, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (_ExchangeDialogBusinessHandler(),
     _ExchangeViewsBusinessHandler(),
     _ExchangeDialogModalBusinessHandler(),
     _DetailedExchangeXPDialogBusinessHandler(),
     _ExchangeBerthsDialogBusinessHandler())


class _ExchangeDialogBusinessHandler(PackageBusinessHandler):
    _ALIAS = VIEW_ALIAS.CONFIRM_EXCHANGE_DIALOG
    _EVENT = ShowDialogEvent.SHOW_EXCHANGE_DIALOG
    _LAYER = WindowLayer.WINDOW

    def __init__(self):
        listeners = ((self._EVENT, self._exchangeDialogHandler),)
        super(_ExchangeDialogBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.DEFAULT)

    def _exchangeDialogHandler(self, event):
        name = 'exchange' + event.meta.getType()
        self.__loadOrUpdateDialog(name, self._ALIAS, event.meta, event.handler)

    def __loadOrUpdateDialog(self, name, alias, meta, handler):
        window = self.findViewByName(self._LAYER, name)
        if window is not None:
            window.updateDialog(meta, handler)
            self.bringViewToFront(name)
        else:
            self.loadViewWithDefName(alias, name, None, meta, handler)
        return


class _ExchangeDialogModalBusinessHandler(_ExchangeDialogBusinessHandler):
    _ALIAS = VIEW_ALIAS.CONFIRM_EXCHANGE_DIALOG_MODAL
    _EVENT = ShowDialogEvent.SHOW_EXCHANGE_DIALOG_MODAL
    _LAYER = WindowLayer.TOP_WINDOW


class _ExchangeViewsBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.EXCHANGE_WINDOW, self.loadViewByCtxEvent), (VIEW_ALIAS.EXCHANGE_WINDOW_MODAL, self.loadViewByCtxEvent), (VIEW_ALIAS.EXCHANGE_XP_WINDOW, self.loadViewByCtxEvent))
        super(_ExchangeViewsBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


class _DetailedExchangeXPDialogBusinessHandler(_ExchangeDialogBusinessHandler):
    _ALIAS = VIEW_ALIAS.EXCHANGE_XP_WINDOW_DIALOG_MODAL
    _EVENT = ShowDialogEvent.SHOW_DETAILED_EXCHANGE_XP_DIALOG
    _LAYER = WindowLayer.TOP_WINDOW


class _ExchangeBerthsDialogBusinessHandler(_ExchangeDialogBusinessHandler):
    _ALIAS = VIEW_ALIAS.CONFIRM_EXCHANGE_BERTHS_DIALOG
    _EVENT = ShowDialogEvent.SHOW_EXCHANGE_BERTHS_DIALOG
    _LAYER = WindowLayer.FULLSCREEN_WINDOW

    def _exchangeDialogHandler(self, event):
        name = 'exchange' + event.meta.getType()
        window = self.findViewByName(self._LAYER, name)
        parent = event.parent if event.parent else None
        if window is not None:
            window.updateDialog(event.meta, event.handler)
            self.bringViewToFront(name)
        else:
            self.loadViewWithDefName(self._ALIAS, name, parent, event.meta, event.handler)
        return
