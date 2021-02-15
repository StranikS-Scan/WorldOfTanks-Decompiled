# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_in_progress_tooltip_view.py
from collections import OrderedDict
from battle_pass_common import BattlePassState, BattlePassConsts
import constants
from constants import ARENA_BONUS_TYPE
from frameworks.wulf import ViewSettings, Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view_model import BattlePassInProgressTooltipViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_by_place_model import RewardPointsByPlaceModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel
from gui.impl.pub import ViewImpl
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_helpers import isSeasonEndingSoon, getFormattedTimeLeft, getSupportedArenaBonusTypeFor
from gui.prb_control.dispatcher import g_prbLoader
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
GAME_MODE_BY_QUEUE_TYPE = {ARENA_BONUS_TYPE.REGULAR: BattlePassInProgressTooltipViewModel.GAME_MODE_RANDOM_BATTLES,
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO: BattlePassInProgressTooltipViewModel.GAME_MODE_BATTLE_ROYALE,
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD: BattlePassInProgressTooltipViewModel.GAME_MODE_BATTLE_ROYALE,
 ARENA_BONUS_TYPE.RANKED: BattlePassInProgressTooltipViewModel.GAME_MODE_RANKED_BATTLES}

class BattlePassInProgressTooltipView(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView())
        settings.model = BattlePassInProgressTooltipViewModel()
        super(BattlePassInProgressTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassInProgressTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassInProgressTooltipView, self)._onLoading(*args, **kwargs)
        gameMode = self.__getCurrentSupportedGameMode()
        with self.getViewModel().transaction() as model:
            if self.__battleRoyaleController.isBattleRoyaleMode():
                self.__updateBattleRoyalePoints(model)
            else:
                items = model.rewardPoints.getItems()
                for points in self.__battlePassController.getPerBattlePoints(gameMode=gameMode):
                    item = RewardPointsModel()
                    item.setTopCount(points.label)
                    item.setPointsWin(points.winPoint)
                    item.setPointsLose(points.losePoint)
                    items.addViewModel(item)

            model.setGameMode(GAME_MODE_BY_QUEUE_TYPE.get(gameMode, BattlePassInProgressTooltipViewModel.GAME_MODE_UNKNOWN))
            curLevel = self.__battlePassController.getCurrentLevel()
            curPoints, limitPoints = self.__battlePassController.getLevelProgression()
            isPostProgression = self.__battlePassController.getState() == BattlePassState.POST
            model.setLevel(curLevel)
            model.setCurrentPoints(curPoints)
            model.setMaxPoints(limitPoints)
            model.setIsBattlePassPurchased(self.__battlePassController.isBought())
            model.setIsPostProgression(isPostProgression)
            model.setCanPlay(self.__battlePassController.canPlayerParticipate())
            timeTillEnd = ''
            if isSeasonEndingSoon() and not self.__battlePassController.isBought():
                timeTillEnd = getFormattedTimeLeft(self.__battlePassController.getSeasonTimeLeft())
            model.setTimeTillEnd(timeTillEnd)
            if isPostProgression:
                self.__getAwards(model.rewardsCommon, curLevel, BattlePassConsts.REWARD_POST)
            else:
                self.__getAwards(model.rewardsCommon, curLevel, BattlePassConsts.REWARD_FREE)
                self.__getAwards(model.rewardsElite, curLevel, BattlePassConsts.REWARD_PAID)

    def __getCurrentSupportedGameMode(self):
        dispatcher = g_prbLoader.getDispatcher()
        queueType = None
        isInUnit = False
        if dispatcher:
            state = dispatcher.getFunctionalState()
            isInUnit = state.isInUnit(state.entityTypeID)
            queueType = dispatcher.getEntity().getQueueType()
        return getSupportedArenaBonusTypeFor(queueType, isInUnit)

    def __getAwards(self, rewardsList, level, bonusType):
        finalLevel = self.__battlePassController.getMaxLevel()
        if level == finalLevel - 1 and bonusType != BattlePassConsts.REWARD_POST:
            freeReward, paidReward = self.__battlePassController.getSplitFinalAwards()
            if bonusType == BattlePassConsts.REWARD_FREE:
                bonuses = freeReward
            else:
                bonuses = paidReward
        else:
            bonuses = self.__battlePassController.getSingleAward(level + 1, bonusType)
        packBonusModelAndTooltipData(bonuses, rewardsList)

    def __updateBattleRoyalePoints(self, model):
        model.setGameMode(BattlePassInProgressTooltipViewModel.GAME_MODE_BATTLE_ROYALE)
        battleRoyaleRewardPoints = model.battleRoyaleRewardPoints
        soloPoints = self.__getBattleRoyalePoints(constants.ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO)
        battleRoyaleRewardPoints.setSoloMode(self.__createBattleRoyalePointsBlock(soloPoints))
        squadPoints = self.__getBattleRoyalePoints(constants.ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD)
        battleRoyaleRewardPoints.setSquadMode(self.__createBattleRoyalePointsBlock(squadPoints))

    def __createBattleRoyalePointsBlock(self, pointsByMode):
        resultArr = Array()
        for value in pointsByMode:
            pointsModel = RewardPointsByPlaceModel()
            place, points = value[0], value[1]
            pointsModel.setPlace(place)
            pointsModel.setPoints(points)
            resultArr.addViewModel(pointsModel)

        return resultArr

    def __getBattleRoyalePoints(self, gameMode):
        config = self.__lobbyContext.getServerSettings().getBattlePassConfig()
        win = config.bonusPointsList(vehTypeCompDescr=None, isWinner=True, gameMode=gameMode)
        lose = config.bonusPointsList(vehTypeCompDescr=None, isWinner=False, gameMode=gameMode)
        placesDict = {}
        for i, _ in enumerate(win):
            points = win[i] + lose[i]
            if points not in placesDict.keys():
                placesDict[points] = [i + 1, i + 1]
            placesDict[points][1] = i + 1

        placesDict = OrderedDict(sorted(placesDict.items(), reverse=True))
        points = []
        for key, value in placesDict.items():
            if key > 0:
                strValue = str(value[0]) if value[0] == value[1] else '{}-{}'.format(str(value[0]), str(value[1]))
                points.append([strValue, key])

        return points
