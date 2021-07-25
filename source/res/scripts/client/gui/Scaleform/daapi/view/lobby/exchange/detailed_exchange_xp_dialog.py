# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/detailed_exchange_xp_dialog.py
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
from gui.Scaleform.daapi.view.lobby.exchange.ExchangeXPWindow import ExchangeXPWindow
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.genConsts.CONFIRM_EXCHANGE_DIALOG_TYPES import CONFIRM_EXCHANGE_DIALOG_TYPES
from gui.shared.events import ShowDialogEvent

class ExchangeXPWindowDialog(ExchangeXPWindow):
    __slots__ = ('handler', 'meta')

    def __init__(self, meta, handler, ctx=None):
        self.handler = handler
        self.meta = meta
        super(ExchangeXPWindowDialog, self).__init__(ctx, needXP=self.meta.getNeedXP())

    def _processResult(self, result, xpExchanged):
        if callable(self.handler):
            if result.success or result.userMsg:
                self.handler((result.success, result, xpExchanged))
                self.destroy()

    def _goToGoldBuy(self, gold):
        super(ExchangeXPWindowDialog, self)._goToGoldBuy(gold)
        if callable(self.handler):
            self.handler((False, None, 0))
        self.destroy()
        return

    def onWindowClose(self):
        if callable(self.handler):
            self.handler((False, None, 0))
        self.destroy()
        return


class ExchangeDetailedXPDialogMeta(IDialogMeta):
    __slots__ = ('__needXP',)

    def __init__(self, needXP):
        self.__needXP = needXP

    def getEventType(self):
        return ShowDialogEvent.SHOW_DETAILED_EXCHANGE_XP_DIALOG

    def getViewScopeType(self):
        return ScopeTemplates.LOBBY_SUB_SCOPE

    def getNeedXP(self):
        return self.__needXP

    @staticmethod
    def getType():
        return CONFIRM_EXCHANGE_DIALOG_TYPES.TYPE_DETAILED_XP_EXCHANGE
