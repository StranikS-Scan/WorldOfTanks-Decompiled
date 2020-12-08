# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_craft_view.py
import logging
from adisp import process
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_craft.ny_craft_regular_config_model import NyCraftRegularConfigModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_craft.ny_craft_tab_type_item_model import NyCraftTabTypeItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_craft_states import NewYearCraftStates
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_craft_view_model import NewYearCraftViewModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from frameworks.wulf import ViewStatus, ViewSettings
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.toy_content import RegularToyContent, MegaToyContent
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.new_year.views.toy_presenter import CraftToyPresenter
from gui.impl.new_year.sound_rtpc_controller import SoundRTPCController
from gui.server_events.awards_formatters import EXTRA_BIG_AWARD_SIZE, AWARDS_SIZES
from helpers import dependency, getLanguageCode, uniprof
from items.components.ny_constants import CustomizationObjects
from new_year.craft_machine import ShardsStorage, FillersStorage, MegaToysStorage, Antiduplicator, MegaDevice, RegularToysBlock, CraftCostBlock, CraftButtonBlock, CraftMonitor, AntiduplicatorState, RANDOM_TOY_PARAM
from new_year.craft_machine.data_nodes import DataNodesHolder
from new_year.ny_constants import TOY_TYPES_BY_OBJECT_WITHOUT_MEGA
from new_year.ny_processor import CraftProcessor
from new_year.ny_toy_info import NewYearCurrentToyInfo
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from uilogging.decorators import simpleLog, loggerEntry, loggerTarget
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
_logger = logging.getLogger(__name__)
_RU_LANGUAGE_CODE = 'ru'
_MAX_SHOW_CRAFT_ITEMS = 5

@loggerTarget(logKey=NY_LOG_KEYS.NY_CRAFT_VIEW, loggerCls=NYLogger)
class NewYearCraftView(NewYearHistoryNavigation):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_craft_view.NewYearCraftView())
        settings.model = NewYearCraftViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearCraftView, self).__init__(settings)
        self.__currentCraftToyID = None
        self.__countCraftDecorations = 0
        self.__colliderLogicModules = None
        return

    @property
    def viewModel(self):
        return super(NewYearCraftView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.ny_regular_toy_tooltip_content.NyRegularToyTooltipContent():
            toyID = event.getArgument('toyID')
            return RegularToyContent(toyID)
        if event.contentID == R.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_content.NyMegaToyTooltipContent():
            toyID = event.getArgument('toyID')
            return MegaToyContent(toyID)
        return NewYearPartsTooltipContent() if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent() else super(NewYearCraftView, self).createToolTipContent(event, contentID)

    @loggerEntry
    @uniprof.regionDecorator(label='ny.craft', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NewYearCraftView, self)._initialize()
        self.viewModel.onCraftBtnClick += self.__onCraftBtnClick
        self.viewModel.onAddCraftDecoration += self.__addCraftDecoration
        with self.viewModel.transaction() as tx:
            self.__buildRegularConfigData(tx.regularConfig)
            tx.setIsRuUserLanguage(getLanguageCode() == _RU_LANGUAGE_CODE)
            tx.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        self.__colliderLogicModules = DataNodesHolder(layersCount=5)
        self.__colliderLogicModules.createNode('megaToysStorage', MegaToysStorage, 0)
        self.__colliderLogicModules.createNode('megaDevice', MegaDevice, 1, self.viewModel.megaDevice)
        self.__colliderLogicModules.createNode('regularToysBlock', RegularToysBlock, 2, self.viewModel.regularConfig)
        self.__colliderLogicModules.createNode('fillersStorage', FillersStorage, 2)
        self.__colliderLogicModules.createNode('antiduplicator', Antiduplicator, 3, self.viewModel.antiduplicator)
        self.__colliderLogicModules.createNode('shardsStorage', ShardsStorage, 3)
        self.__colliderLogicModules.createNode('craftCostBlock', CraftCostBlock, 3, self.viewModel)
        self.__colliderLogicModules.createNode('craftButtonBlock', CraftButtonBlock, 4, self.viewModel)
        self.__colliderLogicModules.createNode('craftMonitor', CraftMonitor, 4, self.viewModel.monitor)

    @uniprof.regionDecorator(label='ny.craft', scope='exit')
    def _finalize(self):
        self.__colliderLogicModules.clear()
        self.__colliderLogicModules = None
        self.viewModel.onCraftBtnClick -= self.__onCraftBtnClick
        self.viewModel.onAddCraftDecoration -= self.__addCraftDecoration
        super(NewYearCraftView, self)._finalize()
        return

    def _getInfoForHistory(self):
        return {}

    @simpleLog(action=NY_LOG_ACTIONS.NY_CRAFT_VIEW_CRAFT_CLICK)
    @process
    def __onCraftBtnClick(self, _=None):
        self.viewModel.setIsCrafting(True)
        toyType, setting, rank = self.__colliderLogicModules.craftCostBlock.getCraftParams()
        useFiller = self.__colliderLogicModules.antiduplicator.getState() == AntiduplicatorState.ACTIVE
        result = yield CraftProcessor(toyType, setting, rank, useFiller).request()
        if self.viewStatus != ViewStatus.LOADED:
            _logger.warning('View is unloaded during craft operation')
            return
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__addToy(result.auxData, useFiller)

    @staticmethod
    def __buildRegularConfigData(model):
        tabTypes = model.getTabTypes()
        tabGroupNames = model.getTabGroupNames()
        randomTabItem = NyCraftTabTypeItemModel()
        randomTabItem.setGroupName(RANDOM_TOY_PARAM)
        randomTabItem.setType(RANDOM_TOY_PARAM)
        tabTypes.addViewModel(randomTabItem)
        tabGroupNames.addString(RANDOM_TOY_PARAM)
        for customizationObject in CustomizationObjects.ALL:
            tabGroupNames.addString(customizationObject)
            for toyType in TOY_TYPES_BY_OBJECT_WITHOUT_MEGA[customizationObject]:
                item = NyCraftTabTypeItemModel()
                item.setGroupName(customizationObject)
                item.setType(toyType)
                tabTypes.addViewModel(item)

    def __addToy(self, toyID, useFiller):
        self.__currentCraftToyID = toyID
        toy = self._itemsCache.items.festivity.getToys().get(self.__currentCraftToyID)
        SoundRTPCController.setLevelToys(toy.getRank())
        if useFiller:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CHARGE_APPLY)
        toyInfo = NewYearCurrentToyInfo(toyID)
        if toyInfo.isMega():
            craftState = NewYearCraftStates.CRAFT_MEGA
        elif useFiller:
            craftState = NewYearCraftStates.CRAFT_REGULAR_WITH_FILLER
        else:
            craftState = NewYearCraftStates.CRAFT_REGULAR
        with self.viewModel.transaction() as model:
            model.setCraftIcon(backport.image(toyInfo.getIcon(size=EXTRA_BIG_AWARD_SIZE if toyInfo.isMega() else AWARDS_SIZES.BIG)))
            model.setCraftState(craftState)

    def __addCraftDecoration(self, _=None):
        toyDescriptor = self._itemsCache.items.festivity.getToys().get(self.__currentCraftToyID)
        self._newYearSounds.setStylesSwitchBox(toyDescriptor.getSetting())
        SoundRTPCController.setLevelToys(toyDescriptor.getRank())
        with self.viewModel.transaction() as model:
            items = model.craftCarousel.getItems()
            item = CraftToyPresenter(toyDescriptor).asSlotViewModel()
            self.__countCraftDecorations += 1
            items.addViewModel(item)
            items.invalidate()
            if self.__countCraftDecorations > _MAX_SHOW_CRAFT_ITEMS:
                hidingItemIndex = self.__countCraftDecorations - _MAX_SHOW_CRAFT_ITEMS - 1
                first = items[hidingItemIndex]
                first.setHideSlot(True)
