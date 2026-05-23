# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/summer_sale/summer_sale_main_view.py
import logging
from account_helpers.AccountSettings import SHOWN_SUMMER_SALE_INTRO
from typing import TYPE_CHECKING
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.game_control.summer_sale_controller import ProductsStates
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.summer_sale.rewards_category_model import RewardsCategoryModel
from gui.impl.gen.view_models.views.lobby.summer_sale.summer_sale_main_view_model import SummerSaleMainViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.loot_box.loot_box_helper import createTooltipLootBoxContentDecorator
from gui.impl.lobby.summer_sale.tooltips.event_currency_tooltip import EventCurrencyTooltip
from gui.impl.lobby.summer_sale.tooltips.random_vehicle_tooltip import RandomVehicleTooltip
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissionsCategories, showMissionsTemporary
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showSummerSaleInfoPage, showSummerSaleIntroWindow, showVehiclePreview, showSummerSaleConfirmView, showHangar
from gui.shop import Origin, showIngameShop
from gui.summer_sale.bonus_packers import getSummerSaleRewardsBonusPacker
from gui.summer_sale.common import ADDITIONAL_COIN, BONUSES_ORDER, MAIN_COIN, SUMMER_SALE_SET_BUYING_LIMIT, getBonusName, getBonusesFromProduct, groupBonusesByName, groupBonusesByProbability, isValidProduct, mergeBonuses
from helpers import dependency
from shared_utils import CONST_CONTAINER, first
from skeletons.gui.game_control import ISummerSaleController
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings
from th_async import th_async
if TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.summer_sale.time_range_model import TimeRangeModel
_logger = logging.getLogger(__name__)

class Sounds(CONST_CONTAINER):
    SOUND_PLACE_HANGAR = 'STATE_hangar_place'
    STATE_TASKS_PREVIEW = 'STATE_hangar_place_tasks_preview'


PREVIEW_VEHICLE_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.SOUND_PLACE_HANGAR, entranceStates={Sounds.SOUND_PLACE_HANGAR: Sounds.STATE_TASKS_PREVIEW}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class SummerSaleMainView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __summerSale = dependency.descriptor(ISummerSaleController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = SummerSaleMainViewModel()
        super(SummerSaleMainView, self).__init__(settings)
        self.__products = {}
        self.__summerSalesSetPrice = 0
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(SummerSaleMainView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SummerSaleMainView, self).createToolTip(event)

    @createTooltipLootBoxContentDecorator()
    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.summer_sale.RandomVehicleTooltip():
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            return RandomVehicleTooltip(lootBoxID)
        if contentID == R.views.lobby.summer_sale.EventCurrencyTooltip():
            tooltipData = self.getTooltipData(event)
            currencyType = tooltipData.get('currencyType')
            return EventCurrencyTooltip(currencyType)
        return super(SummerSaleMainView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _initialize(self, *args, **kwargs):
        super(SummerSaleMainView, self)._initialize(*args, **kwargs)
        if not AccountSettings.getSettings(SHOWN_SUMMER_SALE_INTRO):
            showSummerSaleIntroWindow()

    def _getEvents(self):
        return ((self.viewModel.onStepperCountChange, self.__onStepperCountChange),
         (self.viewModel.onBuyCoinsClick, self.__onBuyCoinsClick),
         (self.viewModel.onInfoClick, self.__onInfoClick),
         (self.viewModel.onPreviewVehicle, self.__onPreviewVehicle),
         (self.viewModel.onOpenShop, self.__onOpenShop),
         (self.viewModel.onOpenQuests, self.__onOpenQuests),
         (self.viewModel.onBuyProductClick, self.__onBuyProductClick),
         (self.viewModel.onClose, self.__onClose),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated))

    def _getListeners(self):
        return ((events.SummerSaleViewEvent.ON_CLOSE_REWARD_VIEW, self.__updateAdditionalCoin, EVENT_BUS_SCOPE.LOBBY),)

    def _getCallbacks(self):
        return (('inventory', self.__onInventoryChanged),)

    def _onLoading(self, *args, **kwargs):
        super(SummerSaleMainView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vmTx:
            self.__updateEventTimeRange(vmTx.eventTimeRange)
            self.__updateBalance(vmTx)
            self.__updateRewards(vmTx)
            self.__updateRandomVehicle(vmTx)
            vmTx.setHoneyCoinsBalance(self.__summerSale.getBalance(ADDITIONAL_COIN))

    def _onLoaded(self, *args, **kwargs):
        super(SummerSaleMainView, self)._onLoaded(*args, **kwargs)
        self.__updateProductsDependentData()

    def __updateEventTimeRange(self, model):
        model.setStart(self.__summerSale.getStartTime())
        model.setEnd(self.__summerSale.getExpiryTime())

    def __updateBalance(self, model=None):
        model.setBumblebeeCoinsBalance(self.__summerSale.getBalance(MAIN_COIN))
        model.setSummerSaleSetProductCode(self.__summerSale.getSummerSaleSetProductCode())

    def __updateRewards(self, model):
        mergedBonuses = self.__getBonuses(self.__summerSale.getSummerSaleSetCategory())
        rewardsCategories = model.getRewards()
        rewardsCategories.clear()
        for probability, bonuses in mergedBonuses.iteritems():
            rewardsCategoryModel = RewardsCategoryModel()
            rewardsCategoryModel.setProbability(probability * 100.0)
            packBonusModelAndTooltipData(sorted(bonuses, key=lambda b: BONUSES_ORDER.get(getBonusName(b), -1)), rewardsCategoryModel.getRewards(), self.__tooltipData, getSummerSaleRewardsBonusPacker(), len(self.__tooltipData))
            rewardsCategories.addViewModel(rewardsCategoryModel)

        rewardsCategories.invalidate()

    def __updateRandomVehicle(self, model):
        model.setIsAnyRandomVehicleObtained(self.__summerSale.isRandomVehicleObtained())

    @adisp_process
    def __updateProductsDependentData(self):
        status, self.__products = yield self.__summerSale.fetchProducts()
        if status == ProductsStates.EMPTY or not self.__products:
            _logger.error('No products available')
            return
        with self.viewModel.transaction() as vmTx:
            self.__updateProducts(vmTx)
            self.__updateSetsPrice(vmTx)
            self.__updateStepperValues(vmTx)
            self.__updateProgressionLevel(vmTx)

    def __updateProducts(self, model):
        products = sorted(self.__products.items(), key=lambda p: self.__summerSale.getProductsOrder().get(p[0], -1))
        bonuses = []
        for productCode, product in products:
            if isValidProduct(productCode, product):
                bonus = first(getBonusesFromProduct(productCode, product))
                if bonus:
                    bonuses.append(bonus)

        productsList = model.getProducts()
        productsList.clear()
        packBonusModelAndTooltipData(bonuses, productsList, self.__tooltipData, getSummerSaleRewardsBonusPacker(), len(self.__tooltipData))
        productsList.invalidate()

    def __updateSetsPrice(self, model):
        self.__summerSalesSetPrice = first((product.get('price', {}).get('amount', 0) for code, product in self.__products.items() if code == self.__summerSale.getSummerSaleSetProductCode()), -1)
        if self.__summerSalesSetPrice <= 0:
            _logger.error('No valid SummerSale set price found')
            return
        model.summerSaleSetsTotalPrice.setCurrency(MAIN_COIN)
        model.summerSaleSetsTotalPrice.setAmount(self.__summerSalesSetPrice * self.__getSetsCountToRepresent())

    def __updateStepperValues(self, model):
        setsCountToRepresent = self.__getSetsCountToRepresent()
        model.stepper.setMaximum(SUMMER_SALE_SET_BUYING_LIMIT)
        model.stepper.setValue(max(1, setsCountToRepresent))
        model.summerSaleSetsTotalPrice.setAmount(self.__summerSalesSetPrice * setsCountToRepresent)

    def __getBonuses(self, category):
        lootBox = first((lb for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == category))
        if lootBox is None:
            _logger.error('No lootbox found')
            return {}
        else:
            bonusSlots = lootBox.getBonusSlots()
            groupedByProbabilityBonuses = groupBonusesByProbability(bonusSlots)
            groupedByNameBonuses = {}
            for probability, bonuses in groupedByProbabilityBonuses.iteritems():
                groupedByNameBonuses[probability] = groupBonusesByName(bonuses)

            return mergeBonuses(groupedByNameBonuses)

    def __updateProgressionLevel(self, model):
        sortedByCoinsPriceProducts = sorted((product for product in model.getProducts() if product.price.getCurrency() == ADDITIONAL_COIN and not product.getInInventory()), key=lambda p: p.price.getAmount())
        coinsBalance = self.__summerSale.getBalance(ADDITIONAL_COIN)
        level = 0
        for index, product in enumerate(sortedByCoinsPriceProducts, 1):
            if product.price.getAmount() <= coinsBalance:
                level = index
                continue
            break

        model.setProgressionLevel(level)

    def __getSetsCountToRepresent(self):
        return max(1, self.__getAvailableSetsCount())

    def __getAvailableSetsCount(self):
        maxCount = int(self.__summerSale.getBalance(MAIN_COIN) / (self.__summerSalesSetPrice or 1))
        return min((SUMMER_SALE_SET_BUYING_LIMIT, maxCount))

    @adisp_process
    def __buyProduct(self, productCode, count):
        isSuccess, productCode = yield self.__summerSale.buyProduct(productCode, count)
        if not isSuccess:
            _logger.error('Failed to buy product: %s', productCode)

    @args2params(int)
    def __onStepperCountChange(self, selectedCount):
        with self.viewModel.transaction() as vmTx:
            vmTx.summerSaleSetsTotalPrice.setAmount(self.__summerSalesSetPrice * selectedCount)
            vmTx.stepper.setValue(selectedCount)

    def __onBuyCoinsClick(self):
        showIngameShop(self.__summerSale.getShopPageUrl(), Origin.MISSIONS)

    @th_async
    @args2params(str, int)
    def __onBuyProductClick(self, productCode, count):
        if productCode == self.__summerSale.getSummerSaleSetProductCode():
            self.__buyProduct(productCode, count)
        else:
            result = yield showSummerSaleConfirmView(productCode)
            if not result.busy:
                isOk, _ = result.result
                if isOk:
                    self.__buyProduct(productCode, count)

    def __onInfoClick(self):
        showSummerSaleInfoPage()

    @args2params(int)
    def __onPreviewVehicle(self, vehicleCD):
        veh = self.__itemsCache.items.getItemByCD(vehicleCD)
        if veh.invID >= 0:
            g_currentVehicle.selectVehicle(veh.invID)
            showHangar()
        else:
            showVehiclePreview(vehicleCD, previewBackCb=showMissionsTemporary, soundSpace=PREVIEW_VEHICLE_SOUND_SPACE, bottomPanelTextData={'uniqueVehicleTitle': ''})

    def __onOpenShop(self):
        showIngameShop(self.__summerSale.getShopPageUrl(), Origin.MISSIONS)

    def __onOpenQuests(self):
        showMissionsCategories()

    def __onInventoryChanged(self, *args, **kwargs):
        with self.viewModel.transaction() as vmTx:
            self.__updateRewards(vmTx)
            self.__updateProducts(vmTx)
            self.__updateRandomVehicle(vmTx)

    def __onClientUpdated(self, *data):
        dynamicCurrencies = data[0].get('cache', {}).get('dynamicCurrencies', {})
        if dynamicCurrencies and dynamicCurrencies.get(MAIN_COIN):
            with self.viewModel.transaction() as vmTx:
                self.__updateBalance(vmTx)
                self.__updateStepperValues(vmTx)

    def __onCacheResync(self, reason, diff):
        with self.viewModel.transaction() as vmTx:
            self.__updateRandomVehicle(vmTx)

    def __updateAdditionalCoin(self, *args):
        with self.viewModel.transaction() as vmTx:
            vmTx.setHoneyCoinsBalance(self.__summerSale.getBalance(ADDITIONAL_COIN))
            self.__updateProgressionLevel(vmTx)

    def __onClose(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), EVENT_BUS_SCOPE.LOBBY)
