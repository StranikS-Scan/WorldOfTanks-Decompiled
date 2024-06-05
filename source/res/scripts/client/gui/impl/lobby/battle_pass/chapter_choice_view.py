# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/chapter_choice_view.py
import logging
from functools import partial
import typing
from ClientSelectableCameraObject import ClientSelectableCameraObject
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, IS_BATTLE_PASS_COLLECTION_SEEN
from battle_pass_common import CurrencyBP, FinalReward, BattlePassConsts
from frameworks.wulf import ViewFlags, ViewSettings, Array
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBattlePassCoinProductsUrl, getBattlePassPointsProductsUrl
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import getInfoPageURL, getStyleForChapter, getVehicleInfoForChapter, getFinalTankmen, getDataByTankman, getAllFinalRewards, isSeasonWithAdditionalBackground, isSeasonWithSpecialTankmenScreen
from gui.collection.collections_helpers import getCollectionRes, loadBattlePassFromCollections
from gui.impl import backport
from gui.impl.auxiliary.collections_helper import fillCollectionModel
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_choice_view_model import ChapterChoiceViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel, ChapterStates, FinalRewardTypes
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import hideVehiclePreview, showBattlePassBuyWindow, showBattlePassHowToEarnPointsView, showBattlePassTankmenVoiceover, showBrowserOverlayView, showCollectionWindow, showHangar, showShop, showStylePreview, showStyleProgressionPreview, showVehiclePreviewWithoutBottomPanel
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, ICollectionsSystemController
from skeletons.gui.shared import IItemsCache
from tutorial.control.game_vars import getVehicleByIntCD
from web.web_client_api.common import ItemPackEntry, ItemPackType
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
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
         (self.viewModel.awardsWidget.onBpcoinClick, self.__showCoinsShop),
         (self.viewModel.awardsWidget.onBpbitClick, self.__showPointsShop),
         (self.viewModel.awardsWidget.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.awardsWidget.showTankmen, self.__showTankmen),
         (self.viewModel.awardsWidget.collectionEntryPoint.openCollection, self.__openCollection),
         (self.viewModel.onClose, self.__close),
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
            self.__updateBalance(model=model)
            self.__updateRewardChoice(model=model)
            self.__updateBPBitCount(model=model)
            self.__updateFreePoints(model=model)
            self.__updateChapters(model.getChapters())
            model.setIsSeasonWithAdditionalBackground(isSeasonWithAdditionalBackground())
            model.setSeasonNum(self.__battlePass.getSeasonNum())
            model.awardsWidget.setIsBpBitEnabled(not self.__battlePass.isHoliday())
            model.awardsWidget.setIsBpCoinEnabled(not self.__battlePass.isHoliday())
            model.awardsWidget.setHasExtra(self.__battlePass.hasExtra())
            model.awardsWidget.setIsBattlePassCompleted(self.__battlePass.isCompleted())
            model.awardsWidget.setIsSpecialVoiceTankmenEnabled(isSeasonWithSpecialTankmenScreen())
            fillCollectionModel(model.awardsWidget.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())

    def __updateChapters(self, chapters):
        chapters.clear()
        for chapterID in sorted(self.__battlePass.getChapterIDs()):
            model = ChapterModel()
            model.setChapterID(chapterID)
            model.setIsBought(self.__battlePass.isBought(chapterID=chapterID))
            model.setIsExtra(self.__battlePass.isExtraChapter(chapterID))
            self.__fillProgression(chapterID, model)
            self.__fillChapterFinalReward(chapterID, model)
            chapters.addViewModel(model)

        chapters.invalidate()

    def __fillVehicle(self, vehicle, model):
        fillVehicleInfo(model.vehicleInfo, vehicle)
        model.setIsVehicleInHangar(vehicle.isInInventory)

    def __fillProgression(self, chapterID, model):
        model.setChapterState(_CHAPTER_STATES.get(self.__battlePass.getChapterState(chapterID)))
        model.setCurrentLevel(self.__battlePass.getLevelInChapter(chapterID) + 1)
        points, maxPoints = self.__battlePass.getLevelProgression(chapterID)
        model.setLevelProgression(_FULL_PROGRESS * points / (maxPoints or _FULL_PROGRESS))

    def __fillChapterFinalReward(self, chapterID, model):
        rewardType = self.__getChapterRewardType(chapterID)
        if rewardType is None:
            return
        else:
            model.setFinalRewardType(rewardType)
            if rewardType == FinalRewardTypes.VEHICLE:
                self.__fillFinalVehicle(chapterID, model)
            elif rewardType == FinalRewardTypes.STYLE:
                self.__fillFinalStyle(chapterID, model)
            elif rewardType == FinalRewardTypes.TANKMAN:
                self.__fillFinalTankmen(chapterID, model)
            return

    def __fillFinalStyle(self, chapterID, model):
        style = getStyleForChapter(chapterID)
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        vehicle = getVehicleByIntCD(vehicleCD)
        model.setStyleName(style.userName)
        self.__fillVehicle(vehicle, model)

    def __fillFinalVehicle(self, chapterID, model):
        vehicle, _ = getVehicleInfoForChapter(chapterID, battlePass=self.__battlePass, awardSource=BattlePassConsts.REWARD_BOTH)
        self.__fillVehicle(vehicle, model)

    def __fillFinalTankmen(self, chapterID, model):
        tankmanNames = Array()
        for rewardSource in (BattlePassConsts.REWARD_FREE, BattlePassConsts.REWARD_PAID):
            for character in getFinalTankmen(chapterID, rewardSource, battlePass=self.__battlePass):
                _, characterName, _, _ = getDataByTankman(character)
                tankmanNames.addString(characterName)

        model.setTankmanNames(tankmanNames)

    def __updateChaptersProgression(self, chapters):
        for chapter in chapters:
            chapterID = chapter.getChapterID()
            self.__fillProgression(chapterID, chapter)

        chapters.invalidate()

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        model.awardsWidget.setBpcoinCount(self.__itemsCache.items.stats.bpcoin)

    @replaceNoneKwargsModel
    def __updateRewardChoice(self, model=None):
        model.awardsWidget.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
        model.awardsWidget.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())

    @replaceNoneKwargsModel
    def __updateBPBitCount(self, model=None):
        model.awardsWidget.setBpbitCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.BIT.value, 0))

    @replaceNoneKwargsModel
    def __updateFreePoints(self, model=None):
        model.setFreePoints(self.__battlePass.getFreePoints())

    def __onPointsUpdated(self, *_):
        with self.viewModel.transaction() as model:
            self.__updateChaptersProgression(model.getChapters())
            self.__updateFreePoints(model=model)
            model.awardsWidget.setIsBattlePassCompleted(self.__battlePass.isCompleted())
            fillCollectionModel(model.awardsWidget.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())

    def __onBpBitUpdated(self, *data):
        if data[0].get('cache', {}).get('dynamicCurrencies', {}).get(CurrencyBP.BIT.value, ''):
            self.__updateBPBitCount()

    def __updateBoughtChapters(self):
        self.__updateChapters(self.viewModel.getChapters())

    def __onCollectionsUpdated(self, *_):
        with self.viewModel.awardsWidget.transaction() as model:
            fillCollectionModel(model.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())

    def __checkBPState(self, *_):
        if self.__battlePass.isPaused():
            showMissionsBattlePass()
            return
        with self.viewModel.transaction() as model:
            model.setIsSeasonWithAdditionalBackground(isSeasonWithAdditionalBackground())
            model.awardsWidget.setIsSpecialVoiceTankmenEnabled(isSeasonWithSpecialTankmenScreen())
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
            self.__switchCamera()
            rewardType = self.__getChapterRewardType(chapterID)
            if rewardType == FinalRewardTypes.VEHICLE:
                self.__showVehiclePreview(chapterID)
            elif rewardType == FinalRewardTypes.STYLE:
                if FinalReward.PROGRESSIVE_STYLE in getAllFinalRewards(chapterID, battlePass=self.__battlePass):
                    self.__showProgressionStylePreview(chapterID)
                else:
                    self.__showStylePreview(chapterID)
            self.destroyWindow()
            return

    @staticmethod
    def __getPreviewCallback():
        return partial(showMissionsBattlePass, R.views.lobby.battle_pass.ChapterChoiceView())

    def __getPreviewItemPack(self):
        return (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),)

    def __showStylePreview(self, chapterID):
        style = getStyleForChapter(chapterID, battlePass=self.__battlePass)
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        showStylePreview(vehicleCD, style=style, itemsPack=self.__getPreviewItemPack(), backCallback=self.__getPreviewCallback())

    def __showProgressionStylePreview(self, chapter):
        style = getStyleForChapter(chapter, battlePass=self.__battlePass)
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        showStyleProgressionPreview(vehicleCD, style, style.getDescription(), self.__getPreviewCallback(), backport.text(R.strings.battle_pass.chapterChoice.stylePreview.backLabel()), styleLevel=style.getMaxProgressionLevel())

    def __showVehiclePreview(self, chapterID):
        vehicle, style = getVehicleInfoForChapter(chapterID, awardSource=BattlePassConsts.REWARD_BOTH)
        styleInfo = getStyleForChapter(chapterID, battlePass=self.__battlePass)
        if styleInfo is not None:
            showStylePreview(vehicle.intCD, style=styleInfo, topPanelData={'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
             'tabIDs': (TabID.VEHICLE, TabID.STYLE),
             'currentTabID': TabID.STYLE,
             'style': styleInfo}, itemsPack=self.__getPreviewItemPack(), backCallback=self.__getPreviewCallback())
        else:
            showVehiclePreviewWithoutBottomPanel(vehicle.intCD, backCallback=self.__getPreviewCallback(), itemsPack=self.__getPreviewItemPack(), style=style)
        return

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

    def __getChapterRewardType(self, chapterID):
        rewardTypes = getAllFinalRewards(chapterID, battlePass=self.__battlePass)
        if FinalReward.VEHICLE in rewardTypes:
            return FinalRewardTypes.VEHICLE
        elif FinalReward.STYLE in rewardTypes or FinalReward.PROGRESSIVE_STYLE in rewardTypes:
            return FinalRewardTypes.STYLE
        elif FinalReward.TANKMAN in rewardTypes:
            return FinalRewardTypes.TANKMAN
        else:
            _logger.error('Final reward types for chapter <%s> do not contain any supported types', chapterID)
            return None

    @staticmethod
    def __switchCamera():
        ClientSelectableCameraObject.switchCamera()
