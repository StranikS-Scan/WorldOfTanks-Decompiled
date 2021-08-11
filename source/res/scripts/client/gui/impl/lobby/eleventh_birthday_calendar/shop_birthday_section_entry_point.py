# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/eleventh_birthday_calendar/shop_birthday_section_entry_point.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBirthdayPageURL
from gui.impl.gen.view_models.views.lobby.eleventh_birthday_calendar.shop_birthday_section_entry_point_view_model import ShopBirthdaySectionEntryPointViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.shared.event_dispatcher import showShop
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isBirthdayEntryPointAvailable(itemsCache=None):
    return itemsCache.items.stats.actualEventCoin > 0


class ShopBirthdaySectionEntryPointView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.eleventh_birthday_calendar.ShopBirthdaySectionEntryPointView())
        settings.flags = flags
        settings.model = ShopBirthdaySectionEntryPointViewModel()
        super(ShopBirthdaySectionEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShopBirthdaySectionEntryPointView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ShopBirthdaySectionEntryPointView, self)._initialize(*args, **kwargs)
        g_clientUpdateManager.addCallbacks({'stats.{}'.format(Currency.EVENT_COIN): self.__updateCoins})
        self.viewModel.openShopBirthdaySection += self.__openShopBirthdaySection
        self.__updateCoins()

    def _finalize(self):
        self.viewModel.openShopBirthdaySection -= self.__openShopBirthdaySection
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        super(ShopBirthdaySectionEntryPointView, self)._finalize()

    def __updateCoins(self, *_):
        with self.viewModel.transaction() as vm:
            vm.setTokenQuantity(self.__itemsCache.items.stats.actualEventCoin)

    def __openShopBirthdaySection(self):
        showShop(getBirthdayPageURL())
