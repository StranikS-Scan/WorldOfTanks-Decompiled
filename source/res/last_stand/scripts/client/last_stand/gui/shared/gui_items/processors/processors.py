# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shared/gui_items/processors/processors.py
import BigWorld
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import formatPrice
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.gui_items.processors import Processor, makeError
from gui.shared.gui_items.processors.plugins import MoneyValidator
from gui.shared.money import Money
from last_stand.gui.shared.gui_items.processors.plugins import CheckArtefact

class OpenArtefactProcessor(Processor):
    MSG_KEY = R.strings.last_stand_system_messages.open_artefact
    MSG_TYPE = SM_TYPE.Information

    def __init__(self, controller, artefactID, isSkipQuest):
        super(OpenArtefactProcessor, self).__init__(plugins=(CheckArtefact(controller, artefactID, isSkipQuest),))
        self._controller = controller
        self._artefactID = artefactID
        self._isSkipQuest = isSkipQuest

    def _request(self, callback):
        BigWorld.player().LSAccountComponent.openArtefact(self._artefactID, self._isSkipQuest, lambda requestID, code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        err = self.MSG_KEY.dyn(errStr)
        errMessage = backport.text(err()) if err.exists() else backport.text(self.MSG_KEY.server_error())
        return makeError(errMessage, SM_TYPE.Error)


class BuyBundleProcessor(Processor):
    MSG_KEY = R.strings.last_stand_system_messages.open_artefact

    def __init__(self, bundleID, price, count):
        super(BuyBundleProcessor, self).__init__(plugins=(MoneyValidator(Money(**{price.currency: price.amount * count})),))
        self._bundleID = bundleID
        self._price = price
        self._count = count

    def _request(self, callback):
        BigWorld.player().LSAccountComponent.buyBundle(self._bundleID, self._count, lambda requestID, code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError(backport.text(self.MSG_KEY.server_error()), SM_TYPE.Error)

    def _successHandler(self, code, ctx=None):
        res = super(BuyBundleProcessor, self)._successHandler(code, ctx)
        self.__pushSuccessMessage()
        return res

    def __pushSuccessMessage(self):
        bundleName = backport.text(R.strings.last_stand_lobby.bundleView.bundle.serviceChannelMessages.dyn(self._bundleID)())
        messageData = {'title': backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.bundlePurchase.title()),
         'description': backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.bundlePurchase.description(), bundle=bundleName),
         'additionalText': backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.bundlePurchase.additionalText(), money=formatPrice(Money(**{self._price.currency: self._price.amount * self._count}), useStyle=True))}
        SystemMessages.pushMessage('', type=SM_TYPE.lsPurchaseBundleForGold, priority=NotificationPriorityLevel.MEDIUM, messageData=messageData)
