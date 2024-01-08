# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/chapter_choice_view.py
from functools import partial
import typing
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, IS_BATTLE_PASS_COLLECTION_SEEN
from battle_pass_common import CurrencyBP, FinalReward
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBattlePassCoinProductsUrl, getBattlePassPointsProductsUrl
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import getAllFinalRewards, getInfoPageURL, getStyleForChapter
from gui.collection.collections_helpers import getCollectionRes, loadBattlePassFromCollections
from gui.impl import backport
from gui.impl.auxiliary.collections_helper import fillCollectionModel
from gui.impl.auxiliary.rewards_helper import setRewards
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_choice_view_model import ChapterChoiceViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel, ChapterStates
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import hideVehiclePreview, showBattlePassBuyWindow, showBattlePassHowToEarnPointsView, showBattlePassTankmenVoiceover, showBrowserOverlayView, showCollectionWindow, showHangar, showShop, showStylePreview, showStyleProgressionPreview
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, ICollectionsSystemController
from skeletons.gui.shared import IItemsCache
from tutorial.control.game_vars import getVehicleByIntCD
from web.web_client_api.common import ItemPackEntry, ItemPackType
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.shared.gui_items.customization.c11n_items import Style
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}
_FULL_PROGRESS = 100

class ChapterChoiceView(ViewImpl):
    __battlePass = dependency.descriptor(IBattlePassController)
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.ChapterChoiceView())
        settings.flags = ViewFlags.VIEW
        settings.model = ChapterChoiceViewModel()
        super(ChapterChoiceView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChapterChoiceView, self).getViewModel()

    def activate(self):
        self._subscribe()
        self._fillModel()

    def deactivate(self):
        self._unsubscribe()

    def _onLoading(self, *args, **kwargs):
        super(ChapterChoiceView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _getEvents(self):
        return ((self.viewModel.onAboutClick, self.__showAboutView),
         (self.viewModel.onChapterSelect, self.__selectChapter),
         (self.viewModel.onPreviewClick, self.__showPreview),
         (self.viewModel.onPointsInfoClick, self.__showPointsInfoView),
         (self.viewModel.onBuyClick, self.__buyBattlePass),
         (self.viewModel.onBpcoinClick, self.__showCoinsShop),
         (self.viewModel.onBpbitClick, self.__showPointsShop),
         (self.viewModel.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.onClose, self.__close),
         (self.viewModel.collectionEntryPoint.openCollection, self.__openCollection),
         (self.viewModel.showTankmen, self.__showTankmen),
         (self.__battlePass.onBattlePassSettingsChange, self.__checkBPState),
         (self.__battlePass.onExtraChapterExpired, self.__checkBPState),
         (self.__battlePass.onPointsUpdated, self.__onPointsUpdated),
         (self.__battlePass.onSelectTokenUpdated, self.__updateRewardChoice),
         (self.__battlePass.onOffersUpdated, self.__updateRewardChoice),
         (self.__battlePass.onSeasonStateChanged, self.__checkBPState),
         (self.__collectionsSystem.onBalanceUpdated, self.__onCollectionsUpdated),
         (self.__collectionsSystem.onServerSettingsChanged, self.__onCollectionsUpdated),
         (self.__battlePass.onBattlePassIsBought, self.__updateBoughtChapters),
         (g_playerEvents.onClientUpdated, self.__onBpBitUpdated))

    def _getCallbacks(self):
        return (('stats.bpcoin', self.__updateBalance),)

    def _getListeners(self):
        return ((events.CollectionsEvent.NEW_ITEM_SHOWN, self.__onCollectionsUpdated, EVENT_BUS_SCOPE.LOBBY),)

    def _fillModel(self):
        with self.viewModel.transaction() as model:
            fillCollectionModel(model.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())
            self.__updateChapters(model.getChapters())
            self.__updateBalance(model=model)
            self.__updateRewardChoice(model=model)
            self.__updateBPBitCount(model=model)
            self.__updateFreePoints(model=model)
            model.setIsBattlePassCompleted(self.__battlePass.isCompleted())
            model.setIsCustomSeason(self.__battlePass.isCustomSeason())
            model.setSpecialVoiceTankmenCount(len(self.__battlePass.getSpecialTankmen()))
            model.setSeasonNum(self.__battlePass.getSeasonNum())

    def __updateChapters(self, chapters):
        chapters.clear()
        for chapterID in sorted(self.__battlePass.getChapterIDs()):
            model = ChapterModel()
            if {FinalReward.PROGRESSIVE_STYLE, FinalReward.STYLE}.intersection(getAllFinalRewards(chapterID)):
                style = getStyleForChapter(chapterID)
                model.setStyleName(style.userName)
                self.__fillVehicle(style, model)
            model.setChapterID(chapterID)
            setRewards(model, chapterID)
            model.setIsBought(self.__battlePass.isBought(chapterID=chapterID))
            model.setIsExtra(self.__battlePass.isExtraChapter(chapterID))
            self.__fillProgression(chapterID, model)
            chapters.addViewModel(model)

        chapters.invalidate()

    def __fillVehicle(self, style, model):
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        vehicle = getVehicleByIntCD(vehicleCD)
        fillVehicleInfo(model.vehicleInfo, vehicle)
        model.setIsVehicleInHangar(vehicle.isInInventory)

    def __fillProgression(self, chapterID, model):
        model.setChapterState(_CHAPTER_STATES.get(self.__battlePass.getChapterState(chapterID)))
        model.setCurrentLevel(self.__battlePass.getLevelInChapter(chapterID) + 1)
        points, maxPoints = self.__battlePass.getLevelProgression(chapterID)
        model.setLevelProgression(_FULL_PROGRESS * points / (maxPoints or _FULL_PROGRESS))

    def __updateChaptersProgression(self, chapters):
        for chapter in chapters:
            chapterID = chapter.getChapterID()
            self.__fillProgression(chapterID, chapter)

        chapters.invalidate()

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        model.setBpcoinCount(self.__itemsCache.items.stats.bpcoin)

    @replaceNoneKwargsModel
    def __updateRewardChoice(self, model=None):
        model.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
        model.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())

    @replaceNoneKwargsModel
    def __updateBPBitCount(self, model=None):
        model.setBpbitCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.BIT.value, 0))

    @replaceNoneKwargsModel
    def __updateFreePoints(self, model=None):
        model.setFreePoints(self.__battlePass.getFreePoints())

    def __onPointsUpdated(self, *_):
        with self.viewModel.transaction() as model:
            self.__updateChaptersProgression(model.getChapters())
            self.__updateFreePoints(model=model)
            model.setIsBattlePassCompleted(self.__battlePass.isCompleted())
            fillCollectionModel(model.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())

    def __onBpBitUpdated(self, *data):
        if data[0].get('cache', {}).get('dynamicCurrencies', {}).get(CurrencyBP.BIT.value, ''):
            self.__updateBPBitCount()

    def __updateBoughtChapters(self):
        self.__updateChapters(self.viewModel.getChapters())

    def __onCollectionsUpdated(self, *_):
        with self.viewModel.transaction() as model:
            fillCollectionModel(model.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())

    def __checkBPState(self, *_):
        if self.__battlePass.isPaused():
            showMissionsBattlePass()
            return
        with self.viewModel.transaction() as model:
            model.setIsCustomSeason(self.__battlePass.isCustomSeason())
            if len(self.__battlePass.getChapterIDs()) != len(self.viewModel.getChapters()):
                self.__updateChapters(model.getChapters())

    @staticmethod
    def __buyBattlePass(_):
        showBattlePassBuyWindow()

    def __showPreview(self, args):
        chapterID = args.get('chapterID')
        if chapterID is None:
            return
        else:
            hideVehiclePreview(back=False)
            style = getStyleForChapter(chapterID, battlePass=self.__battlePass)
            vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
            if self.__battlePass.isExtraChapter(chapterID):
                self.__showStylePreview(style, vehicleCD)
            else:
                self.__showProgressionStylePreview(style, vehicleCD)
            self.destroyWindow()
            return

    def __showStylePreview(self, style, vehicleCD):
        itemsPack = (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),)
        showStylePreview(vehicleCD, style=style, topPanelData={'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
         'tabIDs': (TabID.VEHICLE, TabID.STYLE),
         'currentTabID': TabID.STYLE,
         'style': style}, itemsPack=itemsPack, backCallback=self.__getPreviewCallback())

    @staticmethod
    def __getPreviewCallback():
        return partial(showMissionsBattlePass, R.views.lobby.battle_pass.ChapterChoiceView())

    def __showProgressionStylePreview(self, style, vehicleCD):
        showStyleProgressionPreview(vehicleCD, style, style.getDescription(), self.__getPreviewCallback(), backport.text(R.strings.battle_pass.chapterChoice.stylePreview.backLabel()), styleLevel=style.getMaxProgressionLevel())

    def __selectChapter(self, args):
        chapterID = int(args.get('chapterID', 0))
        showMissionsBattlePass(R.views.lobby.battle_pass.BattlePassProgressionsView(), chapterID)

    @staticmethod
    def __showAboutView():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW)

    def __showPointsInfoView(self):
        showBattlePassHowToEarnPointsView(parent=self.getParentWindow())

    def __takeAllRewards(self):
        self.__battlePass.takeAllRewards()

    @staticmethod
    def __showCoinsShop():
        showShop(getBattlePassCoinProductsUrl())

    @staticmethod
    def __showPointsShop():
        showShop(getBattlePassPointsProductsUrl())

    @staticmethod
    def __close():
        showHangar()

    def __openCollection(self):
        if not AccountSettings.getSettings(IS_BATTLE_PASS_COLLECTION_SEEN):
            AccountSettings.setSettings(IS_BATTLE_PASS_COLLECTION_SEEN, True)
            self.__onCollectionsUpdated()
        backText = backport.text(getCollectionRes(self.__battlePass.getCurrentCollectionId()).featureName())
        backCallback = partial(loadBattlePassFromCollections, R.views.lobby.battle_pass.ChapterChoiceView())
        showCollectionWindow(collectionId=self.__battlePass.getCurrentCollectionId(), backCallback=backCallback, backBtnText=backText)

    @staticmethod
    def __showTankmen():
        showBattlePassTankmenVoiceover()
