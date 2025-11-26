# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/chapter_choice_view.py
import logging
import typing
from battle_pass_common import BattlePassConsts, FinalReward
from frameworks.wulf import Array
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import getAllFinalRewards, getDataByTankman, getFinalTankmen, getInfoPageURL, getStyleForChapter, getVehicleInfoForChapter, isSeasonWithAdditionalBackground, showFinalRewardPreviewBattlePassState
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_choice_view_model import ChapterChoiceViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel, ChapterStates, FinalRewardTypes
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showBattlePass, showBattlePassHowToEarnPointsView, showBrowserOverlayView
from helpers import dependency
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

    @property
    def viewModel(self):
        return super(ChapterChoicePresenter, self).getViewModel()

    def activate(self):
        self._subscribe()

    def deactivate(self):
        self._unsubscribe()

    def updateInitialData(self, **kwargs):
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
         (self.__battlePass.onBattlePassSettingsChange, self.__checkBPState),
         (self.__battlePass.onPointsUpdated, self.__onPointsUpdated),
         (self.__battlePass.onSeasonStateChanged, self.__checkBPState),
         (self.__battlePass.onBattlePassIsBought, self.__updateBoughtChapters))

    def _fillModel(self):
        with self.viewModel.transaction() as model:
            self.__updateFreePoints(model=model)
            self.__updateChapters(model.getChapters())
            model.setIsSeasonWithAdditionalBackground(isSeasonWithAdditionalBackground())
            postProgressionChapterID = self.__battlePass.getPostProgressionChapterID()
            model.setIsPostProgressionUnlocked(self.__battlePass.getChapterState(postProgressionChapterID) != ChapterState.NOT_STARTED)
            model.setSeasonNum(self.__battlePass.getSeasonNum())

    def __updateChapters(self, chapters):
        chapters.clear()
        for chapterID in sorted(self.__battlePass.getMainChapterIDs()):
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
                _, characterName, _, _, _ = getDataByTankman(character)
                tankmanNames.addString(characterName)

        model.setTankmanNames(tankmanNames)

    def __updateChaptersProgression(self, chapters):
        for chapter in chapters:
            chapterID = chapter.getChapterID()
            self.__fillProgression(chapterID, chapter)

        chapters.invalidate()

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
            model.setIsSeasonWithAdditionalBackground(isSeasonWithAdditionalBackground())
            activeChapters = self.__battlePass.getMainChapterIDs()
            if len(activeChapters) != len(self.viewModel.getChapters()):
                self.__updateChapters(model.getChapters())

    def __showPreview(self, args):
        chapterID = args.get('chapterID')
        if chapterID is None:
            return
        else:
            showFinalRewardPreviewBattlePassState(chapterID=chapterID)
            return

    @staticmethod
    def __showAboutView():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BATTLE_PASS_BROWSER)

    def __showPointsInfoView(self):
        showBattlePassHowToEarnPointsView()

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
