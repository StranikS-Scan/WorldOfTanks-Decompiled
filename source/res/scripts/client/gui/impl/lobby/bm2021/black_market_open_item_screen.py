# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/black_market_open_item_screen.py
import BigWorld
from adisp import process
from async import await, async
from constants import Configs
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bm2021.black_market_open_item_screen_model import BlackMarketOpenItemScreenModel, PerfGroup
from gui.impl.lobby.bm2021.tooltips.black_market_info_tooltip import BlackMarketInfoTooltip
from gui.impl.lobby.loot_box.loot_box_helper import getObtainableVehicles, setVehicleDataToModel
from gui.impl.lobby.bm2021.dialogs.black_market_confirm_vehicle import BlackMarketConfirmVehicle
from gui.impl.lobby.bm2021.dialogs.black_market_exit_confirm_dialog import BlackMarketExitConfirmDialog
from gui.impl.lobby.bm2021.dialogs.black_market_next_open_confirm_dialog import BlackMarketNextOpenConfirmDialog
from gui.impl.gen.view_models.common.vehicle_model import VehicleModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import OptionalBlocks
from gui.Scaleform.daapi.view.lobby.vehicle_preview.hangar_switchers import CustomHangars
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.event_dispatcher import showConfigurableVehiclePreview, showBlackMarketOpenItemWindow, showBlackMarketVehicleListWindow, showCurrencyExchangeDialog, showHangar, hideVehiclePreview, showBlackMarketAwardWindow
from gui.shared.gui_items.loot_box import BLACK_MARKET_ITEM_TYPE
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.gui_items.processors.market_items import MarketItemNextOpenProcessor, MarketItemNextOpenRecordsProcessor
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, Money
from helpers import dependency, statistics
from shared_utils import first
from skeletons.gui.game_control import IEventItemsController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_PERF_LIMITS = {3000: PerfGroup.LOW,
 5000: PerfGroup.MEDIUM}

class BlackMarketOpenItemScreen(ViewImpl):
    __slots__ = ('__item', '__rolledRewards', '__soundSpace', '__isRestored')
    __itemsCtrl = dependency.descriptor(IEventItemsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, item, layoutID, soundSpace, isRestored):
        settings = ViewSettings(layoutID)
        settings.model = BlackMarketOpenItemScreenModel()
        self.__item = item
        self.__rolledRewards = {}
        self.__soundSpace = soundSpace
        self.__isRestored = isRestored
        super(BlackMarketOpenItemScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BlackMarketOpenItemScreen, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return BlackMarketInfoTooltip(self.__item)

    def _onLoading(self, *args, **kwargs):
        super(BlackMarketOpenItemScreen, self)._onLoading(*args, **kwargs)
        self.__setInitItemState()

    def _onLoaded(self, *args, **kwargs):
        self.soundManager.startSpace(self.__soundSpace)
        if not self.__rolledRewards and not self.__isRestored:
            self.soundManager.playSound(backport.sound(R.sounds.black_market_item_open()))
        hideVehiclePreview(back=False)

    def _initialize(self, *args, **kwargs):
        super(BlackMarketOpenItemScreen, self)._initialize(*args, **kwargs)
        self.__addListeners()
        BigWorld.worldDrawEnabled(False)

    def _finalize(self):
        self.__removeListeners()
        self.__item = None
        self.__rolledRewards = None
        super(BlackMarketOpenItemScreen, self)._finalize()
        if self.__hangarSpace.spaceInited:
            BigWorld.worldDrawEnabled(True)
            showHangar()
        return

    def __addListeners(self):
        self.__itemsCache.onSyncCompleted += self.__onInventoryResync
        self.viewModel.onNextOpenVehicle += self.onNextOpenVehicle
        self.viewModel.onPickVehicle += self.__onPickVehicle
        self.viewModel.onOpenPreview += self.__onOpenPreview
        self.viewModel.onOpenHangar += self.__onOpenHangar
        self.viewModel.onClose += self.__onClose
        self.viewModel.onChooseVehicle += self.__onChooseVehicle
        self.viewModel.onOpenVehicleList += self.__onOpenVehicleList
        self.viewModel.onOpenExchange += self.__onOpenExchange
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def __removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onInventoryResync
        self.viewModel.onNextOpenVehicle -= self.onNextOpenVehicle
        self.viewModel.onPickVehicle -= self.__onPickVehicle
        self.viewModel.onOpenPreview -= self.__onOpenPreview
        self.viewModel.onOpenHangar -= self.__onOpenHangar
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onChooseVehicle -= self.__onChooseVehicle
        self.viewModel.onOpenVehicleList -= self.__onOpenVehicleList
        self.viewModel.onOpenExchange -= self.__onOpenExchange
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    @async
    def __onOpenExchange(self):
        nextOpenPriceType, nextOpenPrice = self.__item.getReRollPrice(len(self.__rolledRewards))
        moneyArgs = {nextOpenPriceType: nextOpenPrice}
        result = yield await(showCurrencyExchangeDialog(price=ItemPrice(Money(**moneyArgs), Money(**moneyArgs)), parent=self.getParentWindow()))
        if not result.busy and result.result[0]:
            self.onNextOpenVehicle()

    def __onServerSettingsChange(self, diff):
        if Configs.LOOT_BOXES_CONFIG.value in diff:
            if self.__itemsCtrl.getOwnedItemsByType(BLACK_MARKET_ITEM_TYPE) is None:
                self.destroyWindow()
                return
            itemDiff = diff.get(Configs.LOOT_BOXES_CONFIG.value, {}).get(self.__item.getID(), {})
            if itemDiff:
                self.viewModel.setIsItemEnabled(itemDiff.get('enabled', False) and self.__lobbyContext.getServerSettings().isLootBoxesEnabled())
        return

    def __onOpenVehicleList(self):
        showBlackMarketVehicleListWindow(self.__restoreCallback, parent=self.getParentWindow())

    @async
    def onNextOpenVehicle(self):
        nextOpenPriceType, nextOpenPrice = self.__item.getReRollPrice(len(self.__rolledRewards))
        obtainableVehicles = getObtainableVehicles(self.__item)
        result = yield await(showSingleDialogWithResultData(BlackMarketNextOpenConfirmDialog, R.views.lobby.bm2021.dialogs.ConfirmNextOpen(), endDate=self.__item.getAutoOpenTime(), nextOpenPrice=nextOpenPrice, nextOpenPriceType=nextOpenPriceType, slotsNumber=min((len(obtainableVehicles), self.__item.getReRollCount())), parent=self.getParentWindow(), restoreCb=self.__confirmationRestoreCallback))
        if not result.busy and result.result[0]:
            self.__processNextOpenVehicle()

    @process
    def __processNextOpenVehicle(self):
        result = yield MarketItemNextOpenProcessor(self.__item).request()
        if result.success:
            rolledReward = result.auxData.get('rewards')
            self.__rolledRewards.update({result.auxData.get('reRollCount'): rolledReward})
            rolledVehicles = [ first(vehReward.keys()) for vehReward in rolledReward.get('vehicles') ]
            with self.viewModel.transaction() as vm:
                self.__setRolledVehicles(rolledVehicles, vm)
                vm.setIsHangarOpened(True)
                self.__vehicleSelected(rolledVehicles[-1], vm)
        self.viewModel.setIsOperationSuccessfull(result.success)

    @async
    def __onPickVehicle(self, args=None):
        if args is None:
            vehCD = self.viewModel.getChosenVehicleId()
        else:
            vehCD = int(args.get('vehicleId'))
        result = yield await(showSingleDialogWithResultData(BlackMarketConfirmVehicle, R.views.lobby.bm2021.dialogs.BlackMarketConfirmVehicle(), vehicles=[ first(vehicle.keys()) for rewardID in self.__rolledRewards.keys() for vehicle in self.__rolledRewards[rewardID].get('vehicles') ], endDate=self.__item.getAutoOpenTime(), chosenVehicleId=vehCD, parent=self.getParentWindow()))
        if not result.busy and result.result[0]:
            self.__processPickVehicle(vehCD)
        return

    @process
    def __processPickVehicle(self, vehCD=None):
        rollID = first([ rewardID for rewardID, reward in self.__rolledRewards.iteritems() for vehicle in reward.get('vehicles') if first(vehicle.keys()) == vehCD ])
        if rollID is not None:
            result = yield LootBoxOpenProcessor(self.__item, specificRollNumber=rollID).request()
            self.viewModel.setIsOperationSuccessfull(result.success)
            if result.success:
                mergedBonuses = getMergedBonusesFromDicts(result.auxData)
                if 'vehicles' in mergedBonuses:
                    showBlackMarketAwardWindow(first(first(mergedBonuses.get('vehicles'))))
                self.destroyWindow()
        else:
            self.viewModel.setIsOperationSuccessfull(False)
        return

    @process
    def __setInitItemState(self):
        result = yield MarketItemNextOpenRecordsProcessor().request()
        self.viewModel.setIsOperationSuccessfull(result.success)
        if result.success:
            self.__rolledRewards = result.auxData.get('blackMarket').get('rolledRewards')
        obtainableVehicles = getObtainableVehicles(self.__item)
        with self.viewModel.transaction() as vm:
            perfGroup = PerfGroup.HIGH
            ram = BigWorld.getAutoDetectGraphicsSettingsScore(statistics.HARDWARE_SCORE_PARAMS.PARAM_RAM)
            for limit, group in _PERF_LIMITS.iteritems():
                if ram < limit:
                    perfGroup = group
                    break

            vm.setPerfGroup(perfGroup)
            rolledVehicles = [ first(vehicle.keys()) for rewardID in self.__rolledRewards.keys() for vehicle in self.__rolledRewards[rewardID].get('vehicles') ]
            self.__setRolledVehicles(rolledVehicles, vm)
            vm.setSlotsNumber(min((len(obtainableVehicles), self.__item.getReRollCount())))
            vm.setEndDate(self.__item.getAutoOpenTime())
            self.__setStats(vm)
            serverSettings = self.__lobbyContext.getServerSettings()
            vm.setIsItemEnabled(serverSettings.isLootBoxesEnabled() and serverSettings.getLootBoxConfig().get(self.__item.getID(), {}).get('enabled', False))
            if rolledVehicles:
                lastSelectedVehicle = self.__itemsCtrl.getSelectedOption(BLACK_MARKET_ITEM_TYPE) or rolledVehicles[-1]
                self.__vehicleSelected(lastSelectedVehicle, vm)
                vm.setIsHangarOpened(True)
            vm.setIsDataReady(True)

    def __onChooseVehicle(self, args):
        self.__vehicleSelected(int(args.get('vehicleId')), self.viewModel)

    def __onOpenHangar(self):
        self.__processNextOpenVehicle()

    @async
    def __onClose(self):
        result = yield await(showSingleDialogWithResultData(BlackMarketExitConfirmDialog, R.views.lobby.bm2021.dialogs.ConfirmExit(), endDate=self.__item.getAutoOpenTime(), parent=self.getParentWindow()))
        if not result.busy and not result.result[0]:
            return
        self.destroyWindow()

    def __setRolledVehicles(self, rolledVehicles, model):
        vehicleModels = model.getVehicleList()
        for vehicleCD in rolledVehicles:
            vehicleModel = VehicleModel()
            setVehicleDataToModel(vehicleCD, vehicleModel)
            vehicleModels.addViewModel(vehicleModel)

        vehicleModels.invalidate()
        _, nextOpenPrice = self.__item.getReRollPrice(len(vehicleModels))
        model.setNextOpenPrice(nextOpenPrice)

    def __onOpenPreview(self, args):
        showConfigurableVehiclePreview(vehTypeCompDescr=int(args.get('vehicleId')), previewAlias=VIEW_ALIAS.BLACK_MARKET_ITEM_OPEN_SCREEN, hiddenBlocks=OptionalBlocks.ALL, customHangarAlias=CustomHangars.CUSTOMIZATION_HANGAR.value, previewBackCb=self.__restoreCallback)

    def __onInventoryResync(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            self.__setStats(vm)

    def __setStats(self, model):
        model.stats.setCredits(int(self.__itemsCache.items.stats.money.getSignValue(Currency.CREDITS)))
        model.stats.setGold(int(self.__itemsCache.items.stats.money.getSignValue(Currency.GOLD)))
        model.stats.setCrystal(int(self.__itemsCache.items.stats.money.getSignValue(Currency.CRYSTAL)))
        model.stats.setFreeXP(self.__itemsCache.items.stats.freeXP)
        model.stats.setExchangeRate(self.__itemsCache.items.shop.exchangeRate)

    def __vehicleSelected(self, vehicleCD, model):
        self.__itemsCtrl.setSelectedOption(BLACK_MARKET_ITEM_TYPE, vehicleCD)
        model.setChosenVehicleId(vehicleCD)

    @classmethod
    def __restoreCallback(cls):
        if cls.__itemsCtrl.getOwnedItemsByType(BLACK_MARKET_ITEM_TYPE):
            showBlackMarketOpenItemWindow(isRestored=True)
        else:
            showHangar()
        return cls.__guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.bm2021.BlackMarketOpenItemScreen())

    @classmethod
    def __confirmationRestoreCallback(cls):
        view = cls.__restoreCallback()
        if view is not None:
            view.onNextOpenVehicle()
        return view


class BlackMarketOpenItemScreenWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, item, soundSpace, contentResId=R.views.lobby.bm2021.BlackMarketOpenItemScreen(), isRestored=False):
        super(BlackMarketOpenItemScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BlackMarketOpenItemScreen(item, contentResId, soundSpace, isRestored=isRestored))
