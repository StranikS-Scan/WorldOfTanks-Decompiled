# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/shared/processors/early_access_processors.py
import BigWorld
from AccountCommands import CMD_BUY_EARLY_ACCESS_TOKENS
from gui.shared.gui_items.processors import Processor, makeSuccess, makeError
from gui.shared.gui_items.processors.plugins import SyncValidator, MoneyValidator, WalletValidator
from skeletons.gui.game_control import IEarlyAccessController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency

class EarlyAccessEventValidator(SyncValidator):
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def _validate(self):
        return makeError('event_is_not_active') if not self.__earlyAccessCtrl.isEnabled() or self.__earlyAccessCtrl.isPaused() else makeSuccess()


class BuyEarlyAccessTokensProcessor(Processor):
    __slots__ = ('__count',)
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def __init__(self, count, plugins=None):
        super(BuyEarlyAccessTokensProcessor, self).__init__(plugins)
        self.__count = count
        price = self.__count * self.__earlyAccessCtrl.getTokenCost()
        self.addPlugins((EarlyAccessEventValidator(), WalletValidator(), MoneyValidator(price)))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError(backport.text(R.strings.early_access.clientNotifications.buy.fail.body()))

    def _request(self, callback):
        BigWorld.player()._doCmdIntStr(CMD_BUY_EARLY_ACCESS_TOKENS, self.__count, self.__earlyAccessCtrl.getTokenCost().getCurrency(), lambda requestID, resultID, errorStr, ctx=None: self._response(resultID, callback, errorStr, ctx))
        return
