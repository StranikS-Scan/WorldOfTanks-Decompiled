# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/christmas.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins
from helpers import int2roman, isPlayerAccount

class ToysConvertor(Processor):

    def __init__(self, items):
        super(ToysConvertor, self).__init__([plugins.ChristmasAlchemyValidator(items)])
        self.__items = items

    def _errorHandler(self, code, errStr='', ctx=None):
        key = '#system_messages:christmasItem/conversion/errors/%s'
        return makeI18nError('christmasItem/conversion/errors/%s' % errStr) if len(errStr) and key % errStr in SYSTEM_MESSAGES.ALL_ENUM else makeI18nError('christmasItem/conversion/errors/server_error')

    def _successHandler(self, code, ctx=None):
        localKey = 'christmasItem/conversion/success'
        return makeI18nSuccess(localKey, ctx, toyType='', conversionNumber=5)

    def _request(self, callback):
        LOG_DEBUG('--Xmass-- Convert Toys:', self.__items)
        BigWorld.player().christmas.convertToys(self.__items, lambda requestID, code, errStr, extra: self._response(code, callback, errStr=errStr, ctx=extra))


class ChestBonusReceiver(Processor):

    def __init__(self, chests):
        super(ChestBonusReceiver, self).__init__((plugins.ChestsValidator(chests),))

    def _errorHandler(self, code, errStr='', ctx=None):
        key = '#system_messages:christmasChest/open/errors/%s'
        return makeI18nError('christmasChest/open/errors/%s' % errStr) if len(errStr) and key % errStr in SYSTEM_MESSAGES.ALL_ENUM else makeI18nError('christmasChest/open/errors/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('christmasChest/open/success')

    def _request(self, callback):
        BigWorld.player().christmas.openChest(lambda requestID, code, errStr, extra: self._response(code, callback, errStr=errStr))


class ChristmasTreeFiller(Processor):

    def __init__(self, treeState, treeInfo, useConfirmation):
        super(ChristmasTreeFiller, self).__init__()
        self.__treeState = treeState
        self.__treeRaiting = treeInfo['rating']
        self.__treeLvl = treeInfo['level']
        if useConfirmation:
            self.addPlugin(plugins.MessageConfirmator('christmasTreeFill'))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('christmasItem/christmasTreeFill/errors/server_error')

    def _successHandler(self, code, ctx=None):
        localKey = 'christmasItem/christmasTreeFill/success'
        return makeI18nSuccess(localKey, treeLevel=int2roman(self.__treeLvl), treeRaiting=self.__treeRaiting)

    def _request(self, callback):
        if isPlayerAccount():
            LOG_DEBUG('--Xmass-- FillTree', self.__treeState)
            BigWorld.player().christmas.setChristmasTreeFill(self.__treeState, lambda requestID, code, errStr, extra: self._response(code, callback, errStr=errStr))
