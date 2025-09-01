# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/post_progression_view.py
from functools import partial
from enum import IntEnum, unique
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_BATTLE_PASS_COLLECTION_SEEN, LAST_BATTLE_PASS_CYCLES_SEEN, LAST_BATTLE_PASS_POINTS_SEEN
from battle_pass_common import BATTLE_PASS_TICKETS_EVENT, BattlePassConsts, CurrencyBP
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBattlePassCoinProductsUrl, getBattlePassTalerProductsUrl
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import getInfoPageURL
from gui.collection.collections_helpers import loadCollectionsFromBattlePass
from gui.impl.auxiliary.collections_helper import fillCollectionModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_simple_model import ChapterSimpleModel, ChapterStatus
from gui.impl.gen.view_models.views.lobby.battle_pass.level_model import LevelModel
from gui.impl.gen.view_models.views.lobby.battle_pass.post_progression_view_model import PostProgressionStatus, PostProgressionViewModel
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.base.common import ViewID, Views
from gui.shared.event_dispatcher import showBattlePass, showBattlePassHowToEarnPointsView, showBattlePassTankmenVoiceover, showBrowserOverlayView, showHangar, showShop
from helpers import dependency, time_utils
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController, ICollectionsSystemController, ILootBoxSystemController
from skeletons.gui.shared import IItemsCache
_CHAPTER_STATUSES = {ChapterState.ACTIVE: ChapterStatus.ACTIVE,
 ChapterState.COMPLETED: ChapterStatus.COMPLETED,
 ChapterState.PAUSED: ChapterStatus.PAUSED,
 ChapterState.NOT_STARTED: ChapterStatus.NOTSTARTED}

@unique
class _AnimationState(IntEnum):
    NORMAL_STATE = 0
    NEW_PROGRESS_STATE = 1
    NEW_CYCLE_STATE = 2


class PostProgressionPresenter(ViewComponent[PostProgressionViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, *args, **kwargs):
        super(PostProgressionPresenter, self).__init__(R.aliases.battle_pass.PostProgression(), PostProgressionViewModel)
        self.__chapterID = self.__battlePass.getPostProgressionChapterID()
        self.__tankmenScreen = None
        self.__tooltipItems = {}
        self.__animationState = _AnimationState.NORMAL_STATE
        return

    @property
    def viewModel(self):
        return super(PostProgressionPresenter, self).getViewModel()

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            tooltipData = self.__tooltipItems.get(tooltipId)
            return tooltipData

    def activate(self):
        self._subscribe()

    def deactivate(self):
        self._unsubscribe()

    def updateInitialData(self, **kwargs):
        self.__fillModel()

    def onExtraChapterExpired(self):
        self.__checkBattlePassState()

    def _onLoading(self, *args, **kwargs):
        super(PostProgressionPresenter, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        return ((self.viewModel.onOpenInfoPage, self.__showInfoPage),
         (self.viewModel.onOpenPointsInfo, self.__showPointsInfo),
         (self.viewModel.onProgressAchieved, self.__onProgressAchieved),
         (self.viewModel.onCycleCompleted, self.__onCycleCompleted),
         (self.viewModel.awardsWidget.onTakeRewardsClick, self.__claimRewards),
         (self.viewModel.awardsWidget.onBpcoinClick, self.__showCoinsShop),
         (self.viewModel.awardsWidget.showTickets, self.__showTickets),
         (self.viewModel.awardsWidget.showTankmen, self.__showTankmen),
         (self.viewModel.awardsWidget.showTalers, self.__showTalers),
         (self.viewModel.awardsWidget.collectionEntryPoint.openCollection, self.__openCollection),
         (self.__battlePass.onBattlePassSettingsChange, self.__checkBattlePassState),
         (self.__battlePass.onSelectTokenUpdated, self.__updateRewardChoice),
         (self.__battlePass.onOffersUpdated, self.__updateRewardChoice),
         (self.__battlePass.onPointsUpdated, self.__onPointsUpdated),
         (self.__battlePass.onSeasonStateChanged, self.__checkBattlePassState),
         (self.__battlePass.onBattlePassIsBought, self.__onBattlePassBought),
         (self.__collectionsSystem.onBalanceUpdated, self.__updateCollections),
         (self.__collectionsSystem.onServerSettingsChanged, self.__updateCollections),
         (self.__lootBoxes.onStatusChanged, self.__updateTicketInfo),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__updateTicketInfo),
         (self.__lootBoxes.onBoxesCountChanged, self.__updateTicketInfo),
         (g_playerEvents.onClientUpdated, self.__onBPTalerUpdated))

    def _getCallbacks(self):
        return (('stats.bpcoin', self.__updateBalance),)

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            self.__updatePostProgressionData(model=model)
            self.__updateProgression(model=model)
            self.__updateChapters(model.getChapters())
            self.__updateBalance(model=model)
            self.__updateRewardChoice(model=model)
            self.__updateTicketInfo(model=model)
            self.__updateCollections(model=model)
            model.awardsWidget.setIsTalerEnabled(not self.__battlePass.isHoliday())
            model.awardsWidget.setIsBpCoinEnabled(not self.__battlePass.isHoliday())
            model.awardsWidget.setTalerCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.TALER.value, 0))
            model.awardsWidget.setTankmenScreenID(self.__getTankmenScreenID())

    @replaceNoneKwargsModel
    def __updatePostProgressionData(self, model=None):
        model.setChapterID(self.__chapterID)
        endTimestamp = self.__battlePass.getSeasonFinishTime()
        model.setEndDate(time_utils.makeLocalServerTime(endTimestamp))
        model.setPostProgressionStatus(self.__getPostProgressionStatus())

    def __updateChapters(self, chapters):
        chapters.clear()
        for chapterID in sorted(self.__battlePass.getMainChapterIDs()):
            model = ChapterSimpleModel()
            model.setChapterID(chapterID)
            model.setIsBattlePassPurchased(self.__battlePass.isBought(chapterID=chapterID))
            model.setIsRegular(not self.__battlePass.isExtraChapter(chapterID))
            model.setChapterStatus(self.__getChapterStatus(chapterID))
            chapters.addViewModel(model)

        chapters.invalidate()

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        model.awardsWidget.setBpcoinCount(self.__itemsCache.items.stats.bpcoin)

    @replaceNoneKwargsModel
    def __updateRewardChoice(self, model=None):
        model.awardsWidget.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
        model.awardsWidget.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())

    @replaceNoneKwargsModel
    def __updateTicketInfo(self, model=None):
        model.awardsWidget.setIsTicketsEnabled(self.__lootBoxes.isAvailable(BATTLE_PASS_TICKETS_EVENT) and bool(self.__lootBoxes.getActiveBoxes(BATTLE_PASS_TICKETS_EVENT)))
        model.awardsWidget.setTicketsCount(self.__lootBoxes.getBoxesCount(BATTLE_PASS_TICKETS_EVENT))

    @replaceNoneKwargsModel
    def __updateCollections(self, model=None):
        fillCollectionModel(model.awardsWidget.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())

    @replaceNoneKwargsModel
    def __updateProgression(self, model=None):
        currentChapterPoints = self.__battlePass.getPointsInChapter(self.__chapterID)
        currentLevel = self.__battlePass.getLevelByPoints(self.__chapterID, currentChapterPoints)
        currentPoints, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, currentChapterPoints, currentLevel)
        currentLevel += 1
        minLevel, maxLevel = self.__battlePass.getChapterLevelInterval(self.__chapterID)
        currentLevel = currentLevel if currentLevel <= maxLevel else maxLevel
        model.setCurrentLevel(currentLevel)
        model.setCurrentLevelPoints(currentPoints)
        completedCyclesCount = self.__battlePass.getCompletedCyclesCount(self.__chapterID)
        model.setCyclesCompletedCount(completedCyclesCount)
        previousChapterPoints = AccountSettings.getSettings(LAST_BATTLE_PASS_POINTS_SEEN).get(self.__chapterID, 0)
        previousLevel = self.__battlePass.getLevelByPoints(self.__chapterID, previousChapterPoints)
        previousPoints, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, previousChapterPoints, previousLevel)
        previousLevel += 1
        previousLevel = previousLevel if previousLevel <= maxLevel else maxLevel
        model.setPreviousLevel(previousLevel)
        model.setPreviousLevelPoints(previousPoints)
        previousBattlePassCyclesSeen = AccountSettings.getSettings(LAST_BATTLE_PASS_CYCLES_SEEN)
        model.setPreviousCyclesCompletedCount(previousBattlePassCyclesSeen)
        levels = model.getLevels()
        levels.clear()
        for level in range(minLevel, maxLevel + 1):
            levels.addViewModel(self.__getLevelModel(level))

        levels.invalidate()
        self.__animationState = _AnimationState.NORMAL_STATE
        if currentChapterPoints != previousChapterPoints:
            self.__animationState |= _AnimationState.NEW_PROGRESS_STATE
        if completedCyclesCount != previousBattlePassCyclesSeen:
            self.__animationState |= _AnimationState.NEW_CYCLE_STATE
        self.__saveLastProgress()
        self.__saveLastCycle()

    def __getLevelModel(self, level):
        model = LevelModel()
        model.setLevel(level)
        model.setLevelPoints(self.__battlePass.getLevelPoints(self.__chapterID, level - 1))
        bonuses = self.__battlePass.getSingleAward(self.__chapterID, level, BattlePassConsts.REWARD_FREE)
        packBonusModelAndTooltipData(bonuses, model.getRewards(), self.__tooltipItems)
        return model

    def __onPointsUpdated(self, *_):
        with self.viewModel.transaction() as model:
            self.__updatePostProgressionData(model=model)
            self.__updateProgression(model=model)
            self.__updateChapters(model.getChapters())

    @replaceNoneKwargsModel
    def __onBattlePassBought(self, model=None):
        self.__updateChapters(model.getChapters())

    def __onBPTalerUpdated(self, *data):
        if data[0].get('cache', {}).get('dynamicCurrencies', {}).get(CurrencyBP.TALER.value, ''):
            with self.viewModel.awardsWidget.transaction() as model:
                model.setTalerCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.TALER.value, 0))

    def __getPostProgressionStatus(self):
        chapterState = self.__battlePass.getChapterState(self.__chapterID)
        if chapterState == ChapterState.ACTIVE:
            return PostProgressionStatus.UNLOCKED
        return PostProgressionStatus.PAUSED if chapterState == ChapterState.PAUSED else PostProgressionStatus.LOCKED

    def __getChapterStatus(self, chapterID):
        chapterState = self.__battlePass.getChapterState(chapterID)
        return _CHAPTER_STATUSES.get(chapterState, ChapterStatus.NOTSTARTED)

    def __getTankmenScreenID(self):
        tankmenScreens = set((screen for chapter, screen in self.__battlePass.getChapterToTankmenScreen().iteritems() if self.__battlePass.isChapterExists(chapter)))
        if len(tankmenScreens) == 1:
            self.__tankmenScreen = first(tankmenScreens)
            return self.__tankmenScreen
        return False

    def __checkBattlePassState(self, *_):
        if self.__battlePass.isPaused():
            showBattlePass()
            return
        self.__fillModel()

    @staticmethod
    def __showInfoPage():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BATTLE_PASS_BROWSER)

    def __showPointsInfo(self):
        showBattlePassHowToEarnPointsView()

    @staticmethod
    def __showCoinsShop():
        showShop(getBattlePassCoinProductsUrl())

    def __showTickets(self):
        showHangar()
        Views.load(ViewID.MAIN, eventName=BATTLE_PASS_TICKETS_EVENT, backCallback=partial(showBattlePass, R.aliases.battle_pass.PostProgression()))

    def __showTankmen(self):
        showBattlePassTankmenVoiceover(self.__tankmenScreen)

    def __claimRewards(self):
        self.__battlePass.takeAllRewards()

    def __openCollection(self):
        if not AccountSettings.getSettings(IS_BATTLE_PASS_COLLECTION_SEEN):
            AccountSettings.setSettings(IS_BATTLE_PASS_COLLECTION_SEEN, True)
            self.__updateCollections()
        loadCollectionsFromBattlePass(self.layoutID, battlePass=self.__battlePass)

    @staticmethod
    def __showTalers():
        showShop(getBattlePassTalerProductsUrl())

    def __onProgressAchieved(self):
        self.__animationState &= ~_AnimationState.NEW_PROGRESS_STATE
        if self.__animationState == _AnimationState.NORMAL_STATE:
            self.__updateProgression()

    def __onCycleCompleted(self):
        self.__animationState &= ~_AnimationState.NEW_CYCLE_STATE
        currentChapterPoints = self.__battlePass.getPointsInChapter(self.__chapterID)
        currentChapterPoints %= self.__battlePass.getLevelsConfig(self.__chapterID)[-1]
        if self.__animationState == _AnimationState.NORMAL_STATE and not currentChapterPoints:
            self.__updateProgression()

    def __saveLastProgress(self):
        previousBattlePassPointsSeen = AccountSettings.getSettings(LAST_BATTLE_PASS_POINTS_SEEN)
        previousBattlePassPointsSeen[self.__chapterID] = self.__battlePass.getPointsInChapter(self.__chapterID)
        AccountSettings.setSettings(LAST_BATTLE_PASS_POINTS_SEEN, previousBattlePassPointsSeen)

    def __saveLastCycle(self):
        completedCyclesCount = self.__battlePass.getCompletedCyclesCount(self.__chapterID)
        AccountSettings.setSettings(LAST_BATTLE_PASS_CYCLES_SEEN, completedCyclesCount)
