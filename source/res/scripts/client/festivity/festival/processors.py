# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/processors.py
import logging
from festivity.festival.item_info import FestivalItemInfo
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeSuccess
from helpers import dependency
from skeletons.festivity_factory import IFestivityFactory
_logger = logging.getLogger()

def _makeBuyItemSuccess(festItem, cost, ctx):
    fullName = backport.text(R.strings.festival.festivalItem.fullName(), backport.text(festItem.getTypeResID()), backport.text(festItem.getNameResID()))
    return makeSuccess(userMsg=backport.text(R.strings.festival.systemMessages.buyFestItem(), fullName=fullName, tickets=cost), msgType=SM_TYPE.PurchaseForFestTickets, auxData=ctx)


class FestivalBuyItemProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, itemID, parent=None):
        confirmator = [plugins.AsyncDialogConfirmator(dialogs.festivalBuyItem, itemID, parent)]
        super(FestivalBuyItemProcessor, self).__init__(confirmator)
        self.__itemID = itemID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('festival/buyItem/server_error')

    def _successHandler(self, code, ctx=None):
        festItem = FestivalItemInfo(self.__itemID)
        return _makeBuyItemSuccess(festItem, festItem.getCost(), ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy festival item by itemID: %s', self.__itemID)
        self.__festivityFactory.getProcessor().buyFestivalItem(self.__itemID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class SetPlayerCardProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, playerCard, parent=None):
        buyPrices = []
        needBuyItems = []
        for itemID in playerCard:
            festItem = FestivalItemInfo(itemID)
            if not festItem.isInInventory():
                needBuyItems.append(itemID)
                buyPrices.append(festItem.getCost())

        confirmator = []
        if needBuyItems:
            confirmator.append(plugins.AsyncDialogConfirmator(dialogs.festivalApplyPlayerCard, needBuyItems, parent))
        super(SetPlayerCardProcessor, self).__init__(confirmator)
        self.__playerCard = playerCard
        self.__buyPrices = buyPrices

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('festival/setItem/server_error')

    def _successHandler(self, code, ctx=None):
        if self.__buyPrices:
            successMsg = backport.text(R.strings.festival.systemMessages.buyAndApplyFestItems(), tickets=sum(self.__buyPrices), count=len(self.__buyPrices))
            return makeSuccess(successMsg, SM_TYPE.PurchaseForFestTickets, ctx)
        return makeSuccess(userMsg=backport.text(R.strings.festival.systemMessages.applyFestItems()), auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to set player card - %s', self.__playerCard)
        self.__festivityFactory.getProcessor().setPlayerCard(self.__playerCard, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class FestivalBuyPackageProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, packageID, parent=None):
        self.__count = 1
        self.__packageItem = self.__festivityFactory.getController().getPackageByID(packageID)
        self.__dialogConfirmator = plugins.AsyncDialogConfirmator(dialogs.festivalBuyPackage, self.__packageItem, parent)
        super(FestivalBuyPackageProcessor, self).__init__([self.__dialogConfirmator])

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('festival/buyPackage/server_error')

    def _successHandler(self, code, ctx=None):
        firstItem = self.__packageItem.extractedItems[0]
        successMsg = backport.text(R.strings.festival.systemMessages.buyPackages(), userType=firstItem.userType, userName=firstItem.title, count=self.__count, tickets=self.__count * self.__packagePrice)
        return makeSuccess(successMsg, SM_TYPE.PurchaseForFestTickets, ctx)

    def _request(self, callback):
        _, self.__count = self.__dialogConfirmator.getResult()
        self.__packagePrice = self.__packageItem.price
        _logger.debug('Make server request to buy festival package by packageID: %d, count: %d', self.__packageItem.packageID, self.__count)
        self.__festivityFactory.getProcessor().buyFestivalPackage(self.__packageItem.packageID, self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class FestivalBuyRandomItemProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, randomName):
        super(FestivalBuyRandomItemProcessor, self).__init__()
        self.__randomName = randomName
        self.__randomCost = self.__festivityFactory.getController().getRandomCost(randomName)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('festival/buyItem/server_error')

    def _successHandler(self, code, ctx=None):
        festItem = FestivalItemInfo(ctx)
        return _makeBuyItemSuccess(festItem, self.__randomCost, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy random festival item by random name: %s', self.__randomName)
        self.__festivityFactory.getProcessor().buyRandomFestivalItem(self.__randomName, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
