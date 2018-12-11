# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_craft_view.py
import typing
import logging
from collections import namedtuple
from gui.shared.utils import decorators
from frameworks.wulf import ViewFlags
from gui import SystemMessages
from gui.Scaleform.locale.NY import NY
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.views.new_year_craft_view_model import NewYearCraftViewModel
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.toy_content import ToyContent
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundVars, RANDOM_STYLE_BOX
from gui.impl.new_year.views.toy_presenter import CraftToyPresenter
from gui.shared.utils.functions import makeTooltip
from helpers import int2roman, dependency
from helpers.i18n import makeString
from items import ny19
from items.components.ny_constants import ToySettings, ToyTypes, CustomizationObjects, TOY_TYPES_BY_OBJECT, TOY_OBJECTS_IDS_BY_NAME, TOY_TYPE_IDS_BY_NAME, RANDOM_VALUE
from items.ny19 import getObjectByToyType
from new_year.ny_constants import SyncDataKeys
from new_year.ny_processor import CraftProcessor
from new_year.ny_toy_info import NewYear19ToyInfo
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)
_MAX_SHOW_CRAFT_ITEMS = 10
_RANDOM = 'random'
_RANDOM_INDEX = 0
_BreakViewCraftInfo = namedtuple('_BreakViewCraftInfo', ('craftCost', 'desiredToy'))

def createFilter(toyType, setting, rank):
    return (ny19.CONSTS.TOY_TYPE_IDS_BY_NAME.get(toyType, -1) + 1, ny19.CONSTS.TOY_SETTING_IDS_BY_NAME.get(setting, -1) + 1, rank)


def _getToyTypeOffset(toyType):
    return toyType - 1


def _getToySettingOffset(toySetting):
    return toySetting - 1


def _getToyRankOffset(toyRank):
    return RANDOM_VALUE if toyRank == _RANDOM_INDEX else toyRank


def _offsetFilter(toyType, setting, rank):
    return (_getToyTypeOffset(toyType), _getToySettingOffset(setting), _getToyRankOffset(rank))


class NewYearCraftView(NewYearNavigation):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__currentCraftToyID', '__countCraftDecorations', '__prevPrice')

    def __init__(self, layoutID, *args, **kwargs):
        super(NewYearCraftView, self).__init__(layoutID, ViewFlags.LOBBY_SUB_VIEW, NewYearCraftViewModel, *args, **kwargs)
        self.__currentCraftToyID = None
        self.__countCraftDecorations = 0
        self.__prevPrice = 0
        return

    @property
    def viewModel(self):
        return super(NewYearCraftView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.newYearToyTooltipContent:
            toyID = event.getArgument('toyID')
            return ToyContent(toyID)
        return NewYearPartsTooltipContent() if contentID == R.views.newYearPartsTooltipContent else super(NewYearCraftView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: NewYearSoundEvents.TOYS,
         NewYearSoundConfigKeys.EXIT_EVENT: NewYearSoundEvents.TOYS_EXIT,
         NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.TOYS}
        super(NewYearCraftView, self)._initialize(soundConfig)
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onFilterChanged += self.__onFilterChanged
        self.viewModel.onGetPartsBtnClick += self.__onGetPartsBtnClick
        self.viewModel.onCraftBtnClick += self.__onCraftBtnClick
        self.viewModel.onAddCraftDecoration += self.__addCraftDecoration
        self.viewModel.onBackBtnClick += self.__onBackBtnClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        with self.viewModel.transaction() as tx:
            self.__buildFilter(tx)
            self.__buildTooltips(tx)
            self.__updateShards(tx)
            self.__buildSlidersData(tx)
            tx.setBackViewName(self._getBackPageName())

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onFilterChanged -= self.__onFilterChanged
        self.viewModel.onGetPartsBtnClick -= self.__onGetPartsBtnClick
        self.viewModel.onCraftBtnClick -= self.__onCraftBtnClick
        self.viewModel.onAddCraftDecoration -= self.__addCraftDecoration
        self.viewModel.onBackBtnClick -= self.__onBackBtnClick
        self._nyController.onDataUpdated -= self.__onDataUpdated
        NewYearNavigation._setCraftFilter(*self.__getFilters())
        self.viewModel.setDisposeEnabled(True)
        super(NewYearCraftView, self)._finalize()

    def _getInfoForHistory(self):
        return {}

    def __onCloseBtnClick(self, _=None):
        self._goToMainView()

    def __onBackBtnClick(self, *_):
        self._goBack()

    def __onGetPartsBtnClick(self, _=None):
        self._goToBreakView(craftInfo=_BreakViewCraftInfo(self.viewModel.getCraftPrice(), _getToyTypeOffset(self.viewModel.getCurrentTypeIndex())), blur3dScene=True)

    @decorators.process('newYear/buyToyWaiting')
    def __onCraftBtnClick(self, _=None):
        toyType, setting, rank = _offsetFilter(*self.__getFilters())
        craftCost = ny19.calculateCraftCost(toyType, setting, rank)
        if craftCost > self._itemsCache.items.festivity.getShardsCount():
            self.viewModel.setNotEnoughAnimTrigger(not self.viewModel.getNotEnoughAnimTrigger())
            _logger.error('Craft cost more than total shards count in account')
            return
        result = yield CraftProcessor(toyType, setting, rank).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__addToy(result.auxData)

    def __onFilterChanged(self, _=None):
        toyType, setting, rank = _offsetFilter(*self.__getFilters())
        newPrice = ny19.calculateCraftCost(toyType, setting, rank)
        with self.viewModel.transaction() as tx:
            tx.setCraftPrice(newPrice)
            tx.setPriceAnimTrigger(not tx.getPriceAnimTrigger())
        shards = self._itemsCache.items.festivity.getShardsCount()
        if self.__prevPrice <= shards < newPrice:
            self._newYearSounds.playEvent(NewYearSoundEvents.COST_TOYS_NOT_CHANGE)
        self.__prevPrice = newPrice
        self.__setSoundStyles(setting)

    def __onDataUpdated(self, keys):
        with self.viewModel.transaction() as tx:
            if SyncDataKeys.TOY_FRAGMENTS in keys:
                self.__updateShards(tx)

    def __buildFilter(self, model):
        toyType, setting, rank = self._getCraftFilter()
        model.setCurrentTypeIndex(toyType)
        model.setCurrentSettingIndex(setting)
        model.setCurrentLevelIndex(rank)
        self.__prevPrice = ny19.calculateCraftCost(*_offsetFilter(toyType, setting, rank))
        model.setCraftPrice(self.__prevPrice)
        self.__setSoundStyles(_getToySettingOffset(setting))

    def __setSoundStyles(self, settingId):
        if settingId == -1:
            self._newYearSounds.setStylesSwitchBox(RANDOM_STYLE_BOX)
        else:
            self._newYearSounds.setStylesSwitchBox(ToySettings.NEW[settingId])

    @staticmethod
    def __buildTooltips(model):
        levelTooltips = model.getLevelBtnTooltips()
        levelTooltips.addString(makeTooltip(header=NY.CRAFTVIEW_LEVELSSLIDER_RANDOMBTN_TOOLTIP_HEADER, body=NY.CRAFTVIEW_LEVELSSLIDER_RANDOMBTN_TOOLTIP_BODY))
        for idx in xrange(ny19.CONSTS.MAX_COLLECTION_LEVEL):
            levelTooltips.addString(makeTooltip(header=makeString(NY.CRAFTVIEW_LEVELSSLIDER_LEVELBTN_TOOLTIP_HEADER, level=int2roman(idx + 1)), body=NY.CRAFTVIEW_LEVELSSLIDER_LEVELBTN_TOOLTIP_BODY))

        settingTooltips = model.getSettingBtnTooltips()
        settingTooltips.addString(makeTooltip(header=NY.CRAFTVIEW_SETTINGSSLIDER_RANDOMBTN_TOOLTIP_HEADER, body=NY.CRAFTVIEW_SETTINGSSLIDER_RANDOMBTN_TOOLTIP_BODY))
        for setting in ToySettings.NEW:
            settingTooltips.addString(makeTooltip(header=NY.getSetting(setting), body=NY.CRAFTVIEW_SETTINGSSLIDER_SETTINGBTN_TOOLTIP_BODY))

        typeTooltips = model.getTypeBtnTooltips()
        typeTooltips.addString(makeTooltip(header=NY.CRAFTVIEW_TYPESSLIDER_RANDOMBTN_TOOLTIP_HEADER, body=NY.CRAFTVIEW_TYPESSLIDER_RANDOMBTN_TOOLTIP_BODY))
        for decorationType in ToyTypes.ALL:
            typeTooltips.addString(makeTooltip(header=NY.getDecorationType(decorationType), body=NY.CRAFTVIEW_TYPESSLIDER_TYPEBTN_TOOLTIP_BODY))

    @staticmethod
    def __buildSlidersData(model):
        types = model.getDecorationTypes()
        lineByTypeIndices = model.getLineByTypeIndices()
        types.addString(_RANDOM)
        lineByTypeIndices.addNumber(_RANDOM_INDEX)
        for typeName in ToyTypes.ALL:
            types.addString(typeName)
            objectName = getObjectByToyType(typeName)
            lineByTypeIndices.addNumber(TOY_OBJECTS_IDS_BY_NAME[objectName] + 1)

        objects = model.getCustomizationObjects()
        typeByLineIndices = model.getTypeByLineIndices()
        objects.addString(_RANDOM)
        typeByLineIndices.addNumber(_RANDOM_INDEX)
        for objectName in CustomizationObjects.ALL:
            objects.addString(objectName)
            types = TOY_TYPES_BY_OBJECT[objectName]
            typeByLineIndices.addNumber(TOY_TYPE_IDS_BY_NAME[types[0]] + 1)

    def __updateShards(self, model):
        model.setPartsCount(self._itemsCache.items.festivity.getShardsCount())

    def __getFilters(self):
        toyType = self.viewModel.getCurrentTypeIndex()
        setting = self.viewModel.getCurrentSettingIndex()
        rank = self.viewModel.getCurrentLevelIndex()
        return (toyType, setting, rank)

    def __addToy(self, toyID):
        self.__currentCraftToyID = toyID
        toy = self._itemsCache.items.festivity.getToys().get(self.__currentCraftToyID)
        self._newYearSounds.setRTPC(NewYearSoundVars.RTPC_LEVEL_TOYS, toy.getRank())
        self._newYearSounds.playEvent(NewYearSoundEvents.MAKE_TOYS)
        toyInfo = NewYear19ToyInfo(toyID)
        self.viewModel.setCraftIcon(RES_ICONS.getDecorationIcon(toyInfo.getIconName()) or '')

    def __addCraftDecoration(self, _=None):
        toyDescriptor = self._itemsCache.items.festivity.getToys().get(self.__currentCraftToyID)
        self._newYearSounds.setStylesSwitchBox(toyDescriptor.getSetting())
        self._newYearSounds.setRTPC(NewYearSoundVars.RTPC_LEVEL_TOYS, toyDescriptor.getRank())
        self._newYearSounds.playEvent(NewYearSoundEvents.MAKE_TOYS_DOWN)
        with self.viewModel.transaction() as model:
            items = model.craftCarousel.getItems()
            item = CraftToyPresenter(toyDescriptor).asSlotModel(self.__countCraftDecorations)
            self.__countCraftDecorations += 1
            items.addViewModel(item)
            items.invalidate()
            if self.__countCraftDecorations > _MAX_SHOW_CRAFT_ITEMS:
                hidingItemIndex = self.__countCraftDecorations - _MAX_SHOW_CRAFT_ITEMS - 1
                first = items[hidingItemIndex]
                first.setHideSlot(True)
