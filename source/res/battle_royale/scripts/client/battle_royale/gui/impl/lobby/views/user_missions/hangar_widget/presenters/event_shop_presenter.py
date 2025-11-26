# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/user_missions/hangar_widget/presenters/event_shop_presenter.py
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getSteelHunterProductsUrl
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from gui.impl.pub.view_component import ViewComponent
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.shared import IItemsCache
from battle_royale.gui.impl.gen.view_models.views.lobby.views.widget.event_shop_model import EventShopModel

class BattleRoyaleEventShopPresenter(ViewComponent[EventShopModel]):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(BattleRoyaleEventShopPresenter, self).__init__(model=EventShopModel)

    def _getEvents(self):
        return super(BattleRoyaleEventShopPresenter, self)._getEvents() + ((self.__battleRoyaleController.onBalanceUpdated, self.__update),
         (self.__battleRoyaleController.onUpdated, self.__update),
         (self.__battleRoyaleController.onPrimeTimeStatusUpdated, self.__update),
         (self.getViewModel().openShop, self.__onOpenShop))

    def _getCallbacks(self):
        return super(BattleRoyaleEventShopPresenter, self)._getCallbacks() + (('cache.mayConsumeWalletResources', self.__update),)

    def _onLoading(self):
        super(BattleRoyaleEventShopPresenter, self)._onLoading()
        self.__update()

    def __update(self, *_):
        with self.getViewModel().transaction() as model:
            balance = self.__battleRoyaleController.getBRCoinBalance(0)
            model.setBalance(balance)
            model.setIsWGMoneyAvailable(self.__itemsCache.items.stats.mayConsumeWalletResources)

    @staticmethod
    def __onOpenShop():
        showShop(getSteelHunterProductsUrl())
