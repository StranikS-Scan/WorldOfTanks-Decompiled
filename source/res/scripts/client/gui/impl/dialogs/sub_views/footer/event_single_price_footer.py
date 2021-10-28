# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/footer/event_single_price_footer.py
from constants import EVENT
from gui.impl.gen import R
from gui.shared.money import Currency
from helpers import dependency
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from skeletons.gui.shared import IItemsCache
from gui.ClientUpdateManager import g_clientUpdateManager
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.gen.view_models.common.simple_price_model import PriceTypeEnum
from gui.impl.gen.view_models.views.dialogs.sub_views.event_price_view_model import EventPriceViewModel

class EventSinglePrice(ViewImpl):
    __slots__ = ('__text', '__count', '__type', '__shop')
    _itemsCache = dependency.descriptor(IItemsCache)
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, text, count, currencyType, layoutID=R.views.dialogs.sub_views.footer.EventPriceFooter()):
        settings = ViewSettings(layoutID)
        settings.model = EventPriceViewModel()
        super(EventSinglePrice, self).__init__(settings)
        self.__text = text
        self.__count = count
        self.__type = PriceTypeEnum.GOLD if currencyType == EVENT.SHOP.REAL_CURRENCY else PriceTypeEnum.TOKENS
        self.__shop = self._gameEventController.getShop()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EventSinglePrice, self)._onLoading(*args, **kwargs)
        self.__shop.onBundleUnlocked += self._moneyChangeHandler
        self._gameEventController.onRewardBoxKeyUpdated += self.__updateViewModel
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        self.__updateViewModel()

    def _finalize(self):
        super(EventSinglePrice, self)._finalize()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__shop.onBundleUnlocked -= self._moneyChangeHandler
        self._gameEventController.onRewardBoxKeyUpdated -= self.__updateViewModel

    def _moneyChangeHandler(self, *_):
        self.__updateViewModel()

    def __updateViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setText(self.__text)
            vm.setCount(self.__count)
            vm.setCurrencyType(self.__type.value)
            vm.setIsEnought(self.__getIsEnought())

    def __getIsEnought(self):
        if self.__type == PriceTypeEnum.GOLD:
            return self.__count <= self._itemsCache.items.stats.money.get(Currency.GOLD, 0)
        return self.__count <= self.__shop.getKeys() if self.__type == PriceTypeEnum.TOKENS else True
