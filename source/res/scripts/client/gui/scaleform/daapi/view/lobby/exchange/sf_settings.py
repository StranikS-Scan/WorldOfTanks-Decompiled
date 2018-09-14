# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/sf_settings.py
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.exchange.ConfirmExchangeDialog import ConfirmExchangeDialog
    return [GroupedViewSettings(VIEW_ALIAS.CONFIRM_EXCHANGE_DIALOG, ConfirmExchangeDialog, 'confirmExchangeDialog.swf', ViewTypes.WINDOW, 'confirmExchangeDialog', None, ScopeTemplates.LOBBY_SUB_SCOPE)]


def getBusinessHandlers():
    return [ExchangeDialogBusinessHandler()]


class ExchangeDialogBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(ShowDialogEvent.SHOW_EXCHANGE_DIALOG, self.__exchangeDialogHandler)]
        super(ExchangeDialogBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.DEFAULT)

    def __exchangeDialogHandler(self, event):
        name = 'exchange' + event.meta.getType()
        self.__loadOrUpdateDialog(name, VIEW_ALIAS.CONFIRM_EXCHANGE_DIALOG, event.meta, event.handler)

    def __loadOrUpdateDialog(self, name, alias, meta, handler):
        manager = self.app.containerManager
        windowContainer = manager.getContainer(ViewTypes.WINDOW)
        window = windowContainer.getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: name})
        if window is not None:
            window.updateDialog(meta, handler)
            isOnTop = manager.as_isOnTopS(ViewTypes.WINDOW, name)
            if not isOnTop:
                manager.as_bringToFrontS(ViewTypes.WINDOW, name)
        else:
            self.app.loadView(alias, name, meta, handler)
        return
