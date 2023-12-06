# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/rewards_info/ny_collections_rewards_presenter.py
import logging
import typing
import nations
from account_helpers.AccountSettings import NY_OLD_REWARDS_BY_YEAR_VISITED
from adisp import adisp_process
from gui import SystemMessages, GUI_NATIONS_ORDER_INDICES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.new_year_collection_additional import NewYearCollectionAdditional
from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.new_year_collection_style_tab import NewYearCollectionStyleTab
from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_collections_rewards_model import CollectionState
from gui.impl.lobby.new_year.dialogs.album.album_buy_collection_dialog_builder import AlbumCollectionDialogBuilder
from gui.impl.lobby.new_year.rewards_info.rewards_sub_model_presenter import RewardsSubModelPresenter
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.navigation import ViewAliases, NewYearTabCache
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundStates
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from items import new_year
from items.components.ny_constants import YEARS_INFO, MAX_ATMOSPHERE_LVL
from new_year.collection_presenters import COLLECTION_PRESENTER_REGESTRY, getCollectionCost, getAdditionalBonusByCollectionID
from new_year.ny_constants import Collections
from new_year.ny_preview import getVehiclePreviewID
from new_year.ny_processor import BuyCollectionProcessor
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_collections_rewards_model import NyCollectionsRewardsModel
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)

class NyCollectionsRewardsPresenter(RewardsSubModelPresenter):
    __slots__ = ('__tooltips', '__currentStyle', '__yearName', '__collectionName', '__confirmationWindow')
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, model, parentView):
        soundConfig = {NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.REWARDS_COLLECTIONS}
        super(NyCollectionsRewardsPresenter, self).__init__(model, parentView, soundConfig)
        self.__tooltips = {}
        self.__currentStyle = None
        self.__confirmationWindow = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return NewYearPartsTooltipContent() if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent() else None

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return

    def initialize(self, year=Collections.NewYear22, collection=None, *args, **kwargs):
        super(NyCollectionsRewardsPresenter, self).initialize(*args, **kwargs)
        self.viewModel.onCollectionNameChanged += self.__onCollectionNameChanged
        self.viewModel.onGetStyleButton += self.__onGetStyleButton
        self.viewModel.onGoToCollectionButton += self.__onGoToCollectionButton
        self.viewModel.onPreviewStyleButton += self.__onPreviewStyleButton
        self.__nyController.onDataUpdated += self.__onDataUpdated
        self.__invalidate(year, collection)

    def update(self, year=Collections.NewYear22, collection=None, *args, **kwargs):
        self.__invalidate(year, collection)

    def finalize(self):
        if self.__confirmationWindow is not None:
            self.__confirmationWindow.stopWaiting(DialogButtons.CANCEL)
            self.__confirmationWindow = None
        self.viewModel.onCollectionNameChanged -= self.__onCollectionNameChanged
        self.viewModel.onGetStyleButton -= self.__onGetStyleButton
        self.viewModel.onGoToCollectionButton -= self.__onGoToCollectionButton
        self.viewModel.onPreviewStyleButton -= self.__onPreviewStyleButton
        self.__nyController.onDataUpdated -= self.__onDataUpdated
        self.__tooltips.clear()
        self.__currentStyle = None
        super(NyCollectionsRewardsPresenter, self).finalize()
        return

    def getInfoForHistory(self):
        return dict(tabName=self.__yearName, year=self.__yearName, collection=self.__collectionName)

    def __invalidate(self, year, collection):
        self.__yearName = year
        self.__collectionName = collection or YEARS_INFO.getCollectionTypesByYear(year, useMega=True)[0]
        with self.viewModel.transaction() as model:
            self.__updateState(model)
            self.__updateStyleInfo(model)

    def __updateStyleInfo(self, model):
        model.setStyleName('')
        model.setIsPremium(False)
        nationsModel = model.getNations()
        levelsModel = model.getLevels()
        nationsModel.clear()
        levelsModel.clear()
        if self.__currentStyle is not None:
            model.setStyleName(self.__currentStyle.userName)
            for node in self.__currentStyle.descriptor.filter.include:
                if node.nations:
                    sortedNations = sorted(node.nations, key=GUI_NATIONS_ORDER_INDICES.get)
                    for nation in sortedNations:
                        nationsModel.addString(nations.NAMES[nation])

                if node.levels:
                    if node.tags and VEHICLE_TAGS.PREMIUM in node.tags:
                        model.setIsPremium(True)
                    for level in node.levels:
                        levelsModel.addNumber(level)

        nationsModel.invalidate()
        levelsModel.invalidate()
        return

    def __updateState(self, model):
        collectionIntID = self.__getCollectionIntID()
        self.__updateCollections(model)
        self.__updateAdditionalData(model, collectionIntID)
        model.setCurrentCollectionName(self.__collectionName)
        model.setYear(self.__yearName)
        cost = getCollectionCost(self.__yearName, self.__collectionName)
        model.setCost(cost or 0)
        if self.__yearName == YEARS_INFO.CURRENT_YEAR_STR:
            model.setCollectionState(CollectionState.CURRENTYEAR)
        elif self.__itemsCache.items.festivity.getMaxLevel() != MAX_ATMOSPHERE_LVL and cost == 0:
            model.setCollectionState(CollectionState.RECEIVEDEARLIER)
        elif self.__itemsCache.items.festivity.getMaxLevel() != MAX_ATMOSPHERE_LVL:
            model.setCollectionState(CollectionState.MAXLVLNOTREACHED)
        elif cost == 0:
            model.setCollectionState(CollectionState.RECEIVED)
        elif cost > self.__itemsCache.items.festivity.getShardsCount():
            model.setCollectionState(CollectionState.LACKSHARDS)
        else:
            model.setCollectionState(CollectionState.READYTOGET)
        self.__nyController.markPreviousYearTabVisited(self.__yearName, NY_OLD_REWARDS_BY_YEAR_VISITED)

    def __updateAdditionalData(self, model, collectionIntID):
        self.__tooltips.clear()
        self.__currentStyle = None
        additionalsModel = model.getStyleAdditionals()
        additionalsModel.clear()
        for bonus in getAdditionalBonusByCollectionID(collectionIntID):
            for customization in bonus.getCustomizations():
                tooltipId = len(self.__tooltips)
                custItem = bonus.getC11nItem(customization)
                if custItem is not None and custItem.itemTypeID == GUI_ITEM_TYPE.STYLE:
                    self.__currentStyle = custItem
                    model.setStyleTooltipId(tooltipId)
                    self.__tooltips[tooltipId] = self.__getTooltipData(custItem.intCD)
                    continue
                additionalModel = NewYearCollectionAdditional()
                additionalModel.setTooltipId(tooltipId)
                additionalModel.setCount(customization.get('value', 0))
                additionalModel.setItemType(custItem.itemTypeName if custItem is not None else '')
                additionalModel.setName(custItem.userName)
                self.__tooltips[tooltipId] = self.__getTooltipData(custItem.intCD)
                additionalsModel.addViewModel(additionalModel)

        additionalsModel.invalidate()
        return

    def __updateCollections(self, model):
        collectionPresenter = COLLECTION_PRESENTER_REGESTRY.get(self.__yearName)
        styleTabsModel = model.getStyleTabs()
        styleTabsModel.clear()
        for collectionID in collectionPresenter.getCollectionSettingsIDs(useMega=True):
            _, collectionName = new_year.getCollectionByIntID(collectionID)
            collectionModel = NewYearCollectionStyleTab()
            collectionModel.setName(collectionName)
            collectionModel.setYear(self.__yearName)
            collectionModel.setCount(sum(self.__itemsCache.items.festivity.getCollectionDistributions()[collectionID]))
            collectionModel.setTotal(new_year.g_cache.toyCountByCollectionID[collectionID])
            collectionModel.setIsSelected(self.__collectionName == collectionName)
            styleTabsModel.addViewModel(collectionModel)

        styleTabsModel.invalidate()

    def __onCollectionNameChanged(self, args):
        collectionName = args['value']
        self.__invalidate(self.__yearName, collectionName)

    @adisp_process
    def __onGetStyleButton(self, *_):
        collectionID = self.__getCollectionIntID()
        builder = AlbumCollectionDialogBuilder(collectionID)
        builder.setBlur(True)
        self.__confirmationWindow = builder.build()
        result = yield BuyCollectionProcessor(collectionID, self.__confirmationWindow).request()
        self.__confirmationWindow = None
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if not self.isLoaded:
            return
        else:
            with self.viewModel.transaction() as model:
                self.__updateState(model)
            return

    def __onGoToCollectionButton(self, *_):
        self.parentView.goToAlbumView(saveHistory=True, tabName=self.__yearName, state=(NewYearTabCache.PAGE_STATE, {'collectionType': self.__collectionName}))

    def __onPreviewStyleButton(self, *_):
        paramDict = {'instantly': True,
         'withFade': True,
         'viewAlias': ViewAliases.REWARDS_VIEW,
         'objectName': NewYearNavigation.getCurrentObject(),
         'tabName': self.__yearName,
         'collection': self.__collectionName,
         'forceShowMainView': True}
        NewYearNavigation.switchTo(None, True)

        def _backCallback():
            if not self.__nyController.isEnabled():
                event_dispatcher.showHangar()
            else:
                NewYearNavigation.switchFromStyle(**paramDict)

        showStylePreview(getVehiclePreviewID(self.__currentStyle, self.__yearName, self.__collectionName), self.__currentStyle, self.__currentStyle.getDescription(), backCallback=_backCallback, backBtnDescrLabel=backport.text(R.strings.ny.collectionsReward.backLabel()))
        return

    def __onDataUpdated(self, *_):
        with self.viewModel.transaction() as tx:
            self.__updateState(tx)

    def __getCollectionIntID(self):
        collectionStrID = YEARS_INFO.getCollectionSettingID(self.__collectionName, self.__yearName)
        return new_year.g_cache.collections[collectionStrID]

    @staticmethod
    def __getTooltipData(itemCD):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=itemCD))
