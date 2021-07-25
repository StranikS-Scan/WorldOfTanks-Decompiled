# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/exchange_content.py
import logging
from enum import Enum
import Event
from adisp import process, async
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.auxiliary.exchanger import Exchanger
from gui.impl.gen.view_models.common.exchange_panel_model import ExchangePanelModel
from gui.impl.common.base_sub_model_view import BaseSubModelView
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class ExchangeContentResult(Enum):
    IS_OK = 0
    SERVER_ERROR = 1
    INVALID_VALUE = 2


class ExchangeContent(BaseSubModelView):
    __slots__ = ('__fromItem', '__toItem', '__needItem', '__exchanger')

    def __init__(self, fromItem, toItem, viewModel=None, needItem=0):
        super(ExchangeContent, self).__init__(viewModel or ExchangePanelModel())
        self.__fromItem = fromItem
        self.__toItem = toItem
        self.__needItem = needItem
        self.__exchanger = Exchanger(fromItem.getType(), toItem.getType())

    def onLoading(self, *args, **kwargs):
        super(ExchangeContent, self).onLoading(*args, **kwargs)
        fromItemCount = toItemCount = 0
        if self.__needItem > 0:
            fromItemCount, toItemCount = self.__exchanger.calculateFromItemCount(self.__needItem)
        self.__fillItemsModel(fromItemCount, toItemCount)
        self.__fillRateModel()

    def initialize(self, *args, **kwargs):
        super(ExchangeContent, self).initialize(*args, **kwargs)
        self.__exchanger.init()

    def finalize(self):
        self.__exchanger.fini()
        super(ExchangeContent, self).finalize()

    def update(self, needItem=0):
        super(ExchangeContent, self).update()
        self.__needItem = needItem
        fromItemCount = toItemCount = 0
        if self.__needItem > 0:
            fromItemCount, toItemCount = self.__exchanger.calculateFromItemCount(self.__needItem)
        self.__fillItemsModel(fromItemCount, toItemCount)

    @async
    @process
    def exchange(self, callback=None):
        if not self.__validateCount():
            if callback is not None:
                callback(ExchangeContentResult.INVALID_VALUE)
        else:
            fromItemCount = self._viewModel.fromItem.getValue()
            result = yield self.__exchanger.tryExchange(fromItemCount, withConfirm=False)
            if result and result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if callback is not None:
                callback(ExchangeContentResult.SERVER_ERROR if result is None else ExchangeContentResult.IS_OK)
        return

    def getViewModel(self):
        return self._viewModel

    def __validateCount(self):
        fromItemCount = self._viewModel.fromItem.getValue()
        if not self.__fromItem.isEnough(fromItemCount):
            fromItemCount = self.__fromItem.getMaxCount()
        toItemCount = self._viewModel.toItem.getValue()
        validToItemCount = self.__exchanger.calculateToItemCount(fromItemCount)
        valid = validToItemCount == toItemCount and self.__fromItem.isAvailable() and self.__toItem.isAvailable()
        if validToItemCount != toItemCount:
            self.__fillItemsModel(fromItemCount, validToItemCount)
        return valid

    def __fillItemsModel(self, fromItemCount, toItemCount):
        with self._viewModel.transaction() as ts:
            self.__fromItem.updateItemModel(ts.fromItem, fromItemCount)
            self.__toItem.updateItemModel(ts.toItem, toItemCount)

    def __fillRateModel(self):
        with self._viewModel.transaction() as ts:
            ts.exchangeRate.setCurrent(self.__exchanger.getCurrentRate())
            ts.exchangeRate.setDefault(self.__exchanger.getDefaultRate())
            ts.exchangeRate.setDiscount(self.__exchanger.getDiscount())


class ExchangeItemInfo(object):

    def __init__(self, itemType=''):
        self._type = itemType
        self.onUpdated = Event.Event()

    def init(self):
        pass

    def fini(self):
        self.onUpdated.clear()

    def getType(self):
        return self._type

    def isEnough(self, count):
        return False

    def getMaxCount(self):
        pass

    def isAvailable(self):
        return False

    def getItemModel(self, count):
        return None

    def _onUpdate(self, *args, **kwargs):
        self.onUpdated()


class ExchangeMoneyInfo(ExchangeItemInfo):
    __itemsCache = dependency.descriptor(IItemsCache)
    __walletController = dependency.descriptor(IWalletController)

    def __init__(self, currencyType=''):
        if currencyType not in Currency.ALL:
            _logger.error('%s is not Currency!', currencyType)
        super(ExchangeMoneyInfo, self).__init__(itemType=currencyType)

    def init(self):
        super(ExchangeMoneyInfo, self).init()
        g_clientUpdateManager.addMoneyCallback(self._onUpdate)
        self.__walletController.onWalletStatusChanged += self._onUpdate

    def fini(self):
        self.__walletController.onWalletStatusChanged -= self._onUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeMoneyInfo, self).fini()

    def isEnough(self, count):
        return count <= self.__itemsCache.items.stats.money.get(self._type, 0)

    def isAvailable(self):
        return self.__walletController.isAvailable

    def getMaxCount(self):
        return self.__itemsCache.items.stats.money.get(self._type, 0)

    def updateItemModel(self, viewModel, count):
        viewModel.setName(self._type)
        viewModel.setValue(count)
        viewModel.setIsEnough(self.isEnough(count))
