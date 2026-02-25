# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/chapter_choice_view.py
import logging
import typing
from battle_pass_common import BattlePassConsts, FinalReward, isPostProgressionChapter, NON_CHAPTER_ID
from frameworks.wulf import Array
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_constants import ChapterState, MIN_LEVEL
from gui.battle_pass.battle_pass_helpers import getAllFinalRewards, getDataByTankman, getFinalTankmen, getInfoPageURL, getStyleForChapter, getVehicleInfoForChapter, showFinalRewardPreviewBattlePassState, getTimeExpirations
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_choice_view_model import ChapterChoiceViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel, ChapterStates, FinalRewardTypes
from gui.impl.gui_decorators import args2params
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showBattlePass, showBattlePassHowToEarnPointsView, showBrowserOverlayView, showBattlePassTankmenVoiceover
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from tutorial.control.game_vars import getVehicleByIntCD
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}
_FULL_PROGRESS = 100

class ChapterChoicePresenter(ViewComponent[ChapterChoiceViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(ChapterChoicePresenter, self).__init__(R.aliases.battle_pass.ChapterChoice(), ChapterChoiceViewModel)
        self.__chapterID = kwargs.get('selectedChapter', 0)

    @property
    def viewModel(self):
        return super(ChapterChoicePresenter, self).getViewModel()

    def activate(self):
        self._subscribe()

    def deactivate(self):
        self._unsubscribe()

    def updateInitialData(self, **kwargs):
        self.__chapterID = kwargs.get('selectedChapter', 0)
        self._fillModel()

    def onExtraChapterExpired(self):
        self.__checkBPState()

    def _onLoading(self, *args, **kwargs):
        super(ChapterChoicePresenter, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _getEvents(self):
        return ((self.viewModel.onAboutClick, self.__showAboutView),
         (self.viewModel.onPreviewClick, self.__showPreview),
         (self.viewModel.onPointsInfoClick, self.__showPointsInfoView),
         (self.viewModel.onChapterSelect, self.__updateSelectedChapter),
         (self.viewModel.showTankmen, self.__showTankmen),
         (self.__battlePass.onBattlePassSettingsChange, self.__checkBPState),
         (self.__battlePass.onPointsUpdated, self.__onPointsUpdated),
         (self.__battlePass.onSeasonStateChanged, self.__checkBPState),
         (self.__battlePass.onBattlePassIsBought, self.__updateBoughtChapters))

    def _fillModel(self):
        with self.viewModel.transaction() as model:
            self.__updateFreePoints(model=model)
            self.__updateChapters(model.getChapters())
            self.__chapterID = self.__selectChapter(self.__chapterID)
            model.setSelectedChapter(self.__chapterID)
            postProgressionChapterID = self.__battlePass.getPostProgressionChapterID()
            model.setIsPostProgressionUnlocked(self.__battlePass.getChapterState(postProgressionChapterID) != ChapterState.NOT_STARTED)
            model.setSeasonNum(self.__battlePass.getSeasonNum())

    def __selectChapter(self, chapterID):
        if chapterID == NON_CHAPTER_ID:
            if self.__battlePass.getCurrentChapterID() == NON_CHAPTER_ID:
                if any((not self.__battlePass.isChapterCompleted(ch) for ch in self.__battlePass.getExtraChapterIDs())):
                    return self.__chooseMainChapter(self.__battlePass.getExtraChapterIDs())
                return self.__chooseMainChapter(self.__battlePass.getMainChapterIDs())
            return self.__battlePass.getCurrentChapterID()
        return chapterID if self.__battlePass.isChapterExists(chapterID) else self.__selectChapter(NON_CHAPTER_ID)

    def __chooseMainChapter(self, chapters):
        chaptersByPoints = sorted(chapters, key=self.__battlePass.getPointsInChapter, reverse=True)
        return findFirst(lambda ch: self.__battlePass.getChapterState(ch) != ChapterState.COMPLETED, chaptersByPoints)

    @args2params(int)
    def __updateSelectedChapter(self, chapterID):
        self.__chapterID = chapterID
        self.getParentView().updateSelectedChapter(self.__chapterID)

    def __updateChapters(self, chapters):
        chapters.clear()
        for chapterID in sorted(self.__battlePass.getChapterIDs()):
            model = ChapterModel()
            model.setChapterID(chapterID)
            model.setIsBought(self.__battlePass.isBought(chapterID=chapterID))
            model.setIsExtra(self.__battlePass.isExtraChapter(chapterID))
            model.setIsPostProgression(isPostProgressionChapter(chapterID))
            model.setTankmenScreenID(self.__battlePass.getTankmenScreenID(chapterID))
            model.setChapterRewardsCount(self.__getChapterRewardsCount(chapterID))
            self.__setExpirations(chapterID, model)
            self.__fillProgression(chapterID, model)
            self.__fillChapterFinalReward(chapterID, model)
            chapters.addViewModel(model)

        chapters.invalidate()

    def __fillVehicle(self, vehicle, model):
        fillVehicleInfo(model.vehicleInfo, vehicle)
        model.setIsVehicleInHangar(vehicle.isInInventory)

    def __fillProgression(self, chapterID, model):
        maxLevel = self.__battlePass.getMaxLevelInChapter(chapterID)
        if chapterID == self.__battlePass.getPostProgressionChapterID():
            model.setCyclesCompletedCount(self.__battlePass.getCompletedCyclesCount(chapterID))
            _, maxLevel = self.__battlePass.getChapterLevelInterval(chapterID)
        model.setMaxLevel(maxLevel)
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
            if rewardType == FinalRewardTypes.VEHICLESTYLE:
                self.__fillFinalVehicleStyle(chapterID, model)
            elif rewardType == FinalRewardTypes.VEHICLE:
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

    def __fillFinalVehicleStyle(self, chapterID, model):
        vehicle, _ = getVehicleInfoForChapter(chapterID, battlePass=self.__battlePass, awardSource=BattlePassConsts.REWARD_BOTH)
        self.__fillVehicle(vehicle, model)
        style = getStyleForChapter(chapterID)
        model.setStyleName(style.userName)

    def __fillFinalTankmen(self, chapterID, model):
        tankmanNames = Array()
        for rewardSource in (BattlePassConsts.REWARD_FREE, BattlePassConsts.REWARD_PAID):
            for character in getFinalTankmen(chapterID, rewardSource, battlePass=self.__battlePass):
                _, characterName, _, _, _ = getDataByTankman(character)
                tankmanNames.addString(characterName)

        model.setTankmanNames(tankmanNames)

    def __updateChaptersProgression(self, chapters):
        for chapter in chapters:
            chapterID = chapter.getChapterID()
            self.__fillProgression(chapterID, chapter)
            self.__fillChapterFinalReward(chapterID, chapter)

        chapters.invalidate()

    def __setExpirations(self, chapterID, model):
        endTimestamp, timeLeft = getTimeExpirations(chapterID)
        model.setExpireTime(endTimestamp)
        model.setTimeLeft(timeLeft)

    @replaceNoneKwargsModel
    def __updateFreePoints(self, model=None):
        model.setFreePoints(self.__battlePass.getFreePoints())

    def __onPointsUpdated(self, *_):
        with self.viewModel.transaction() as model:
            self.__updateChaptersProgression(model.getChapters())
            self.__updateFreePoints(model=model)

    def __updateBoughtChapters(self):
        self.__updateChapters(self.viewModel.getChapters())

    def __checkBPState(self, *_):
        if self.__battlePass.isPaused():
            showBattlePass()
            return
        with self.viewModel.transaction() as model:
            activeChapters = self.__battlePass.getChapterIDs()
            if len(activeChapters) != len(self.viewModel.getChapters()):
                self.__chapterID = self.__selectChapter(self.__chapterID)
                model.setSelectedChapter(self.__chapterID)
            self.__updateChapters(model.getChapters())

    @args2params(int)
    def __showPreview(self, chapterID):
        showFinalRewardPreviewBattlePassState(chapterID=chapterID)

    @staticmethod
    def __showAboutView():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BATTLE_PASS_BROWSER)

    def __showPointsInfoView(self):
        showBattlePassHowToEarnPointsView()

    def __getChapterRewardType(self, chapterID):
        if isPostProgressionChapter(chapterID):
            return FinalRewardTypes.POSTPROGRESSION
        else:
            rewardTypes = getAllFinalRewards(chapterID, battlePass=self.__battlePass)
            if FinalReward.VEHICLE in rewardTypes:
                if FinalReward.STYLE in rewardTypes:
                    return FinalRewardTypes.VEHICLESTYLE
                return FinalRewardTypes.VEHICLE
            if FinalReward.STYLE in rewardTypes or FinalReward.PROGRESSIVE_STYLE in rewardTypes:
                return FinalRewardTypes.STYLE
            if FinalReward.TANKMAN in rewardTypes:
                return FinalRewardTypes.TANKMAN
            _logger.error('Final reward types for chapter <%s> do not contain any supported types', chapterID)
            return None

    def __showTankmen(self, args):
        chapterID = args.get('chapterID')
        showBattlePassTankmenVoiceover(self.__battlePass.getTankmenScreenID(chapterID))

    def __getChapterRewardsCount(self, chapterID):
        bonuses = self.__battlePass.getPackedAwardsInterval(chapterID, MIN_LEVEL, self.__battlePass.getMaxLevelInChapter(chapterID), BattlePassConsts.REWARD_PAID)
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return len(BattlePassAwardsManager.sortBonuses(bonuses))
