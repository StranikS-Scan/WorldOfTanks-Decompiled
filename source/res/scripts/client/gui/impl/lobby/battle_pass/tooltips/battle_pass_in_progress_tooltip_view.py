# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_in_progress_tooltip_view.py
from collections import OrderedDict
from battle_pass_common import BattlePassConsts
import constants
from frameworks.wulf import ViewSettings, Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view_model import BattlePassInProgressTooltipViewModel, ChapterType
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_by_place_model import RewardPointsByPlaceModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel
from gui.impl.pub import ViewImpl
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_helpers import getChapterType, isSeasonEndingSoon, getFormattedTimeLeft, getSupportedCurrentArenaBonusType
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.formatters.invites import getPreQueueName
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext

class BattlePassInProgressTooltipView(ViewImpl):
    __battlePass = dependency.descriptor(IBattlePassController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__battleType',)

    def __init__(self, battleType=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView())
        settings.model = BattlePassInProgressTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__battleType = battleType
        super(BattlePassInProgressTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassInProgressTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassInProgressTooltipView, self)._onLoading(*args, **kwargs)
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is None:
            return
        else:
            battleType = self.__battleType or prbDispatcher.getEntity().getQueueType()
            with self.getViewModel().transaction() as model:
                if self.__battleRoyaleController.isBattleRoyaleMode():
                    self.__updateBattleRoyalePoints(model)
                else:
                    items = model.rewardPoints.getItems()
                    arenaBonusType = getSupportedCurrentArenaBonusType(battleType)
                    for points in self.__battlePass.getPerBattlePoints(gameMode=arenaBonusType):
                        item = RewardPointsModel()
                        item.setTopCount(points.label)
                        item.setPointsWin(points.winPoint)
                        item.setPointsLose(points.losePoint)
                        items.addViewModel(item)

                curLevel = self.__battlePass.getCurrentLevel()
                chapterID = self.__battlePass.getCurrentChapterID()
                curPoints, limitPoints = self.__battlePass.getLevelProgression(chapterID)
                expireTime = self.__battlePass.getChapterRemainingTime(chapterID)
                if self.__battlePass.isHoliday():
                    expireTime = self.__battlePass.getSeasonTimeLeft()
                isBattlePassPurchased = self.__battlePass.isBought(chapterID=chapterID)
                model.setLevel(curLevel)
                model.setChapter(chapterID)
                model.setCurrentPoints(curPoints)
                model.setMaxPoints(limitPoints)
                model.setIsBattlePassPurchased(isBattlePassPurchased)
                if battleType:
                    model.setBattleType(getPreQueueName(battleType).lower())
                model.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
                model.setExpireTime(expireTime)
                model.setChapterType(ChapterType(getChapterType(self.__battlePass.getCurrentChapterID())))
                timeTillEnd = ''
                if isSeasonEndingSoon() and not isBattlePassPurchased:
                    timeTillEnd = getFormattedTimeLeft(self.__battlePass.getSeasonTimeLeft())
                model.setTimeTillEnd(timeTillEnd)
                self.__getAwards(chapterID, model.rewardsCommon, curLevel, BattlePassConsts.REWARD_FREE)
                self.__getAwards(chapterID, model.rewardsElite, curLevel, BattlePassConsts.REWARD_PAID)
            return

    def __getAwards(self, chapterID, rewardsList, level, bonusType):
        bonuses = self.__battlePass.getSingleAward(chapterID, level + 1, bonusType)
        packBonusModelAndTooltipData(bonuses, rewardsList)

    def __updateBattleRoyalePoints(self, model):
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
