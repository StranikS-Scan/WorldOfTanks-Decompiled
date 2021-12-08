# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/ny_craft_view.py
import logging
from adisp import process
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_regular_config_model import NyCraftRegularConfigModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_tab_type_item_model import NyCraftTabTypeItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_tab_type_model import NyCraftTabTypeModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_view_model import NyCraftViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_states import NyCraftStates
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_mega_decoration_tooltip import NyMegaDecorationTooltip
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.views.toy_presenter import CraftToyPresenter
from helpers import dependency
from helpers.server_settings import serverSettingsChangeListener
from items.components.ny_constants import FillerState, CustomizationObjects, TOY_TYPES_BY_OBJECT_WITH_RANDOM
from gui.impl.lobby.new_year.craft.components import Antiduplicator, CraftButtonBlock, CraftCostBlock, CraftMonitor, FillersStorage, MegaDevice, MegaToysStorage, RegularToysBlock, ShardsStorage
from gui.impl.lobby.new_year.craft.components.data_nodes import DataNodesHolder
from new_year.collection_presenters import CurrentNYCollectionPresenter
from new_year.ny_constants import SyncDataKeys
from new_year.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_processor import CraftProcessor
from new_year.ny_toy_info import NewYearCurrentToyInfo
from realm import CURRENT_REALM
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)
_RU_LANGUAGE_CODE = 'ru'
_MAX_SHOW_CRAFT_ITEMS = 5

class NyCraftView(HistorySubModelPresenter):
    __slots__ = ('__logicModules', '__currentCraftToyID', '__lastCollectionSize', '__atmospherePoints')
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NyCraftView, self).__init__(viewModel, parentView, *args, **kwargs)
        self.__logicModules = None
        self.__currentCraftToyID = None
        self.__lastCollectionSize = 0
        self.__atmospherePoints = 0
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.lobby.new_year.tooltips
        toyID = event.getArgument('toyID')
        if event.contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            return NyDecorationTooltip(toyID, isPureToy=True)
        if event.contentID == R.views.lobby.new_year.tooltips.NyMegaDecorationTooltip():
            return NyMegaDecorationTooltip(toyID, isPureToy=True)
        return NewYearPartsTooltipContent() if contentID == tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent() else super(NyCraftView, self).createToolTipContent(event, contentID)

    def initialize(self, *args, **kwargs):
        super(NyCraftView, self).initialize()
        with self.viewModel.transaction() as tx:
            self.__buildRegularConfigData(tx.regularConfig)
            tx.setRealm(CURRENT_REALM)
            tx.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        self.__logicModules = DataNodesHolder(layersCount=6)
        self.__logicModules.createNode('megaToysStorage', MegaToysStorage, 0)
        self.__logicModules.createNode('megaDevice', MegaDevice, 1, self.viewModel.megaDevice)
        self.__logicModules.createNode('regularToysBlock', RegularToysBlock, 2, self.viewModel.regularConfig)
        self.__logicModules.createNode('fillersStorage', FillersStorage, 2)
        self.__logicModules.createNode('shardsStorage', ShardsStorage, 4)
        self.__logicModules.createNode('antiduplicator', Antiduplicator, 3, self.viewModel.antiduplicator)
        self.__logicModules.createNode('craftCostBlock', CraftCostBlock, 4, self.viewModel)
        self.__logicModules.createNode('craftButtonBlock', CraftButtonBlock, 5, self.viewModel)
        self.__logicModules.createNode('craftMonitor', CraftMonitor, 5, self.viewModel.monitor)
        self.__atmospherePoints, _ = NewYearAtmospherePresenter.getLevelProgress()

    def finalize(self):
        self.__logicModules.clear()
        self.__logicModules = None
        self.viewModel.craftCarousel.getItems().clear()
        super(NyCraftView, self).finalize()
        return

    def _getEvents(self):
        return ((self._nyController.onDataUpdated, self.__onDataUpdated), (self.viewModel.onCraftBtnClick, self.__onCraftBtnClick), (self.viewModel.onAddCraftDecoration, self.__onAddCraftDecoration))

    def _getInfoForHistory(self):
        return {}

    @serverSettingsChangeListener(SyncDataKeys.LEVEL, SyncDataKeys.POINTS)
    def __onDataUpdated(self, *_):
        atmospherePoints, _ = NewYearAtmospherePresenter.getLevelProgress()
        atmospherePointsAmount = atmospherePoints - self.__atmospherePoints
        if atmospherePointsAmount:
            self.viewModel.setAtmospherePoints(atmospherePointsAmount)
        self.__atmospherePoints = atmospherePoints

    @process
    def __onCraftBtnClick(self, *_):
        self.viewModel.setIsCrafting(True)
        self.__logicModules.updateCrafting(isInProgress=True)
        toyType, setting, rank = self.__logicModules.craftCostBlock.getCraftParams()
        fillerState = self.__logicModules.antiduplicator.getState()
        self.__lastCollectionSize = CurrentNYCollectionPresenter.getCount()
        result = yield CraftProcessor(toyType, setting, rank, fillerState.value).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if not self.isLoaded:
            return
        self.__logicModules.updateCrafting(isInProgress=False)
        self.viewModel.setIsCrafting(False)
        if result.success:
            self.__addToy(result.auxData, fillerState)

    def __addToy(self, toyID, fillerState):
        self.__currentCraftToyID = toyID
        toyInfo = NewYearCurrentToyInfo(toyID)
        if toyInfo.isMega():
            craftState = NyCraftStates.CRAFT_MEGA
        elif fillerState.isActive:
            craftState = NyCraftStates.CRAFT_REGULAR_WITH_FILLER
        else:
            craftState = NyCraftStates.CRAFT_REGULAR
        with self.viewModel.transaction() as model:
            model.setCraftIconName(toyInfo.getIconName())
            model.setCraftState(craftState)

    def __onAddCraftDecoration(self, *_):
        toyDescriptor = self._itemsCache.items.festivity.getToys().get(self.__currentCraftToyID)
        NewYearSoundsManager.setStylesSwitchBox(toyDescriptor.getSetting())
        with self.viewModel.transaction() as model:
            items = model.craftCarousel.getItems()
            item = CraftToyPresenter(toyDescriptor).asSlotViewModel()
            if CurrentNYCollectionPresenter.getCount() > self.__lastCollectionSize and not self.__nyController.isMaxAtmosphereLevel():
                atmospherePoints = NewYearAtmospherePresenter.getAtmPointsForNewToy(self.__currentCraftToyID)
                item.setAtmosphereBonus(atmospherePoints)
            items.addViewModel(item)
            items.invalidate()

    @staticmethod
    def __buildRegularConfigData(model):
        tabTypes = model.getTabsTypes()
        tabTypes.clear()
        for customizationObject in CustomizationObjects.WITH_RANDOM:
            newTab = NyCraftTabTypeModel()
            newTab.setName(customizationObject)
            newTabTypes = newTab.getTypes()
            for toyType in TOY_TYPES_BY_OBJECT_WITH_RANDOM[customizationObject]:
                item = NyCraftTabTypeItemModel()
                item.setType(toyType)
                item.setGroupName(customizationObject)
                newTabTypes.addViewModel(item)

            tabTypes.addViewModel(newTab)
