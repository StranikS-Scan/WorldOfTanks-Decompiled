# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_collections_reward_view.py
import logging
import nations
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewStatus, ViewSettings
from gui import SystemMessages, GUI_NATIONS_ORDER_INDICES
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipDataByBonus
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_collection_additional import NewYearCollectionAdditional
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_collection_style_tab import NewYearCollectionStyleTab
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_collections_reward_view_model import NewYearCollectionsRewardViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_nation_flag_model import NewYearNationFlagModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import ViewAliases, NewYearTabCache
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from helpers import dependency
from items.components.ny_constants import YEARS_INFO, ToySettings, MAX_ATMOSPHERE_LVL
from new_year.collection_presenters import COLLECTION_PRESENTER_REGESTRY, getCollectionCost, getAdditionalBonusByCollectionID
from new_year.ny_constants import Collections, SyncDataKeys
from new_year.ny_processor import BuyCollectionProcessor
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from skeletons.gui.shared import IItemsCache
from items import new_year
from gui.impl import backport
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundStates
from uilogging.decorators import simpleLog, loggerTarget, loggerEntry
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
DEFAULT_VEH_ID = 6929
MAP_VEH_ID = {(Collections.NewYear18, ToySettings.SOVIET): 7169,
 (Collections.NewYear18, ToySettings.ASIAN): 6193,
 (Collections.NewYear18, ToySettings.MODERN_WESTERN): 3937,
 (Collections.NewYear18, ToySettings.TRADITIONAL_WESTERN): 6209}
_logger = logging.getLogger(__name__)

@loggerTarget(loggerCls=NYLogger, logKey=NY_LOG_KEYS.NY_COLLECTION_REWARDS_VIEW)
class NewYearCollectionsRewardView(NewYearHistoryNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _navigationAlias = ViewAliases.REWARDS_VIEW
    _isScopeWatcher = False

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_collections_reward_view.NewYearCollectionsRewardView())
        settings.flags = ViewFlags.VIEW
        settings.model = NewYearCollectionsRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearCollectionsRewardView, self).__init__(settings)
        self.__additionalData = {}
        self.__currentStyle = None
        self.__styleTooltipData = None
        return

    def createToolTipContent(self, event, contentID):
        return NewYearPartsTooltipContent() if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent() else super(NewYearCollectionsRewardView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            typeName = event.getArgument('type')
            if typeName == 'style':
                window = BackportTooltipWindow(self.__styleTooltipData, self.getParentWindow())
            else:
                tooltipId = event.getArgument('tooltipId')
                window = BackportTooltipWindow(self.__additionalData[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(NewYearCollectionsRewardView, self).createToolTip(event)

    @property
    def viewModel(self):
        return super(NewYearCollectionsRewardView, self).getViewModel()

    def invalidate(self, year, collection=None):
        if self.viewStatus != ViewStatus.LOADED:
            return
        self.__invalidate(year, collection)

    @loggerEntry
    def _initialize(self, year=Collections.NewYear21, collection=None):
        soundConfig = {NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.REWARDS_COLLECTIONS}
        super(NewYearCollectionsRewardView, self)._initialize(soundConfig)
        self.viewModel.onCollectionNameChanged += self.__onCollectionNameChanged
        self.viewModel.onGetStyleButton += self.__onGetStyleButton
        self.viewModel.onGoToCollectionButton += self.__onGoToCollectionButton
        self.viewModel.onPreviewStyleButton += self.__onPreviewStyleButton
        self._nyController.onDataUpdated += self.__onDataUpdated
        self.__invalidate(year, collection)
        self.viewModel.setCurrentYear(YEARS_INFO.CURRENT_YEAR_STR)

    def _finalize(self):
        self.viewModel.onCollectionNameChanged -= self.__onCollectionNameChanged
        self.viewModel.onGetStyleButton -= self.__onGetStyleButton
        self.viewModel.onGoToCollectionButton -= self.__onGoToCollectionButton
        self.viewModel.onPreviewStyleButton -= self.__onPreviewStyleButton
        self._nyController.onDataUpdated -= self.__onDataUpdated
        super(NewYearCollectionsRewardView, self)._finalize()

    def _getInfoForHistory(self):
        return dict(tabName=self.__yearName, year=self.__yearName, collection=self.__collectionName)

    def __invalidate(self, year, collection):
        self.__yearName = year
        self.__collectionName = collection or YEARS_INFO.getCollectionTypesByYear(year, useMega=True)[0]
        with self.viewModel.transaction() as model:
            self.__updateState(model)
            self.__updateStyleInfo(model)
            self.__updateStatus(model)

    def __onCollectionNameChanged(self, args):
        collectionName = args['value']
        self.__invalidate(self.__yearName, collectionName)

    @decorators.process('newYear/buyCollectionWaiting')
    @simpleLog(action=NY_LOG_ACTIONS.NY_GET_COLLECTION_BUTTON_CLICK)
    def __onGetStyleButton(self, *_):
        result = yield BuyCollectionProcessor(self.__getCollectionIntID(), self.getParentWindow()).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if self.viewStatus != ViewStatus.LOADED:
            return
        with self.viewModel.transaction() as model:
            self.__updateCost(model)

    @simpleLog(action=NY_LOG_ACTIONS.NY_GO_TO_COLLECTION_BUTTON_CLICK)
    def __onGoToCollectionButton(self, *_):
        self._goToAlbumView(saveHistory=True, tabName=self.__yearName, stateInfo=(NewYearTabCache.PAGE_STATE, {'typeName': self.__collectionName}))

    @simpleLog(action=NY_LOG_ACTIONS.NY_PREVIEW_STYLE_BUTTON_CLICK)
    def __onPreviewStyleButton(self, *_):
        paramDict = self._getInfoForHistory()
        paramDict['viewAlias'] = ViewAliases.REWARDS_VIEW
        paramDict['objectName'] = self.getCurrentObject()
        self._resetObject()
        showStylePreview(self.__getVehiclePreviewID(self.__currentStyle), self.__currentStyle, self.__currentStyle.getDescription(), lambda *_: NewYearHistoryNavigation.showMainView(**paramDict), backBtnDescrLabel=backport.text(R.strings.ny.collectionsReward.backLabel()))

    def __getVehiclePreviewID(self, style):
        styledVehicleCD = None
        if g_currentVehicle.isPresent() and style.mayInstall(g_currentVehicle.item):
            styledVehicleCD = g_currentVehicle.item.intCD
        else:
            accDossier = self._itemsCache.items.getAccountDossier()
            vehiclesStats = accDossier.getRandomStats().getVehicles()
            vehicleGetter = self._itemsCache.items.getItemByCD
            sortedVehicles = sorted((vehicleGetter(veh) for veh in vehiclesStats.iterkeys()), key=lambda veh: (veh.level, vehiclesStats[veh.intCD].battlesCount), reverse=True)
            for vehicle in sortedVehicles:
                if style.mayInstall(vehicle):
                    styledVehicleCD = vehicle.intCD
                    break

        if styledVehicleCD is None:
            styledVehicleCD = MAP_VEH_ID.get((self.__yearName, self.__collectionName), DEFAULT_VEH_ID)
        return styledVehicleCD

    def __updateStyleInfo(self, model):
        model.setIsAllNations(True)
        model.setIsAllLevels(True)
        model.setIsPremium(False)
        model.compatibleNations.clear()
        levels = []
        if self.__currentStyle is not None:
            for node in self.__currentStyle.descriptor.filter.include:
                if node.nations:
                    model.setIsAllNations(False)
                    sortedNations = sorted(node.nations, key=GUI_NATIONS_ORDER_INDICES.get)
                    for nation in sortedNations:
                        flag = NewYearNationFlagModel()
                        flag.setNation(nations.NAMES[nation])
                        model.compatibleNations.addViewModel(flag)

                if node.levels:
                    model.setIsAllLevels(False)
                    if node.tags and VEHICLE_TAGS.PREMIUM in node.tags:
                        model.setIsPremium(True)
                    for level in node.levels:
                        levels.append(formatRomanNumber(level))

            model.compatibleNations.invalidate()
        else:
            _logger.warning('Empty currentStyle!')
        levelStr = ''
        if levels:
            sep = backport.text(R.strings.ny.collectionsReward.commaLevels() if len(levels) > 2 else R.strings.ny.collectionsReward.andLevels())
            levelStr = backport.text(R.strings.ny.collectionsReward.lastLevel(), level=sep.join(levels))
        model.setLevels(levelStr)
        return

    def __updateState(self, model):
        collectionIntID = self.__getCollectionIntID()
        self.__updateCollectionState(model)
        self.__updateAdditionalData(model, collectionIntID)
        self.__updateCost(model)
        model.setCurrentCollectionName(self.__collectionName)
        model.setYear(self.__yearName)

    def __updateAdditionalData(self, model, collectionIntID):
        self.__additionalData.clear()
        model.styleAdditionals.clear()
        for idx, bonus in enumerate(getAdditionalBonusByCollectionID(collectionIntID)):
            custItem = self._itemsCache.items.getItemByCD(bonus.specialArgs[0])
            if custItem is not None and custItem.itemTypeID == GUI_ITEM_TYPE.STYLE:
                self.__currentStyle = custItem
                self.__styleTooltipData = createTooltipDataByBonus(bonus)
                continue
            additionalModel = NewYearCollectionAdditional()
            additionalModel.setId(idx)
            additionalModel.setCount(bonus.label)
            additionalModel.setItemType(custItem.itemTypeName if custItem is not None else '')
            self.__additionalData[idx] = createTooltipDataByBonus(bonus)
            model.styleAdditionals.addViewModel(additionalModel)

        model.styleAdditionals.invalidate()
        return

    def __updateCollectionState(self, model):
        collectionPresenter = COLLECTION_PRESENTER_REGESTRY.get(self.__yearName)
        model.styleTabs.clear()
        for collectionID in collectionPresenter.getCollectionSettingsIDs(useMega=True):
            _, collectionName = new_year.getCollectionByIntID(collectionID)
            collectionModel = NewYearCollectionStyleTab()
            collectionModel.setName(collectionName)
            collectionModel.setYear(self.__yearName)
            collectionModel.setCount(sum(self._itemsCache.items.festivity.getCollectionDistributions()[collectionID]))
            collectionModel.setTotal(new_year.g_cache.toyCountByCollectionID[collectionID])
            collectionModel.setIsSelected(self.__collectionName == collectionName)
            model.styleTabs.addViewModel(collectionModel)

        model.styleTabs.invalidate()

    def __updateCost(self, model):
        cost = getCollectionCost(self.__yearName, self.__collectionName)
        model.setCost(cost or 0)
        model.setIsEnough(cost <= self._itemsCache.items.festivity.getShardsCount())

    def __updateStatus(self, model):
        model.setIsMaxLvl(self._itemsCache.items.festivity.getMaxLevel() == MAX_ATMOSPHERE_LVL)

    def __onDataUpdated(self, keys):
        with self.viewModel.transaction() as tx:
            if SyncDataKeys.TOY_FRAGMENTS in keys:
                self.__updateCost(tx)
            if SyncDataKeys.TOY_COLLECTION in keys:
                self.__updateCollectionState(tx)

    def __getCollectionIntID(self):
        collectionStrID = YEARS_INFO.getCollectionSettingID(self.__collectionName, self.__yearName)
        return new_year.g_cache.collections[collectionStrID]
