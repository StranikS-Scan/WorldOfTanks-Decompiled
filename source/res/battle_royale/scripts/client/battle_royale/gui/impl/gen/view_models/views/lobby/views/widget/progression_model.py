# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/widget/progression_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.leaderboard_reward_tooltip_model import LeaderboardRewardTooltipModel

class ProgressionStatus(IntEnum):
    DISABLED = 0
    ACTIVE = 1


class ProgressionModel(ViewModel):
    __slots__ = ('showProgression', 'onProgressionAnimationCompleted')

    def __init__(self, properties=12, commands=2):
        super(ProgressionModel, self).__init__(properties=properties, commands=commands)

    @property
    def leaderBoard(self):
        return self._getViewModel(0)

    @staticmethod
    def getLeaderBoardType():
        return LeaderboardRewardTooltipModel

    def getStatus(self):
        return ProgressionStatus(self._getNumber(1))

    def setStatus(self, value):
        self._setNumber(1, value.value)

    def getStage(self):
        return self._getNumber(2)

    def setStage(self, value):
        self._setNumber(2, value)

    def getPrevStage(self):
        return self._getNumber(3)

    def setPrevStage(self, value):
        self._setNumber(3, value)

    def getCurPoints(self):
        return self._getNumber(4)

    def setCurPoints(self, value):
        self._setNumber(4, value)

    def getPrevPoints(self):
        return self._getNumber(5)

    def setPrevPoints(self, value):
        self._setNumber(5, value)

    def getStageProgress(self):
        return self._getNumber(6)

    def setStageProgress(self, value):
        self._setNumber(6, value)

    def getPrevStageProgress(self):
        return self._getNumber(7)

    def setPrevStageProgress(self, value):
        self._setNumber(7, value)

    def getStagePoints(self):
        return self._getNumber(8)

    def setStagePoints(self, value):
        self._setNumber(8, value)

    def getPrevStagePoints(self):
        return self._getNumber(9)

    def setPrevStagePoints(self, value):
        self._setNumber(9, value)

    def getIsCompleted(self):
        return self._getBool(10)

    def setIsCompleted(self, value):
        self._setBool(10, value)

    def getTimeTillEnd(self):
        return self._getNumber(11)

    def setTimeTillEnd(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(ProgressionModel, self)._initialize()
        self._addViewModelProperty('leaderBoard', LeaderboardRewardTooltipModel())
        self._addNumberProperty('status', ProgressionStatus.DISABLED.value)
        self._addNumberProperty('stage', 0)
        self._addNumberProperty('prevStage', 0)
        self._addNumberProperty('curPoints', 0)
        self._addNumberProperty('prevPoints', 0)
        self._addNumberProperty('stageProgress', 0)
        self._addNumberProperty('prevStageProgress', 0)
        self._addNumberProperty('stagePoints', 0)
        self._addNumberProperty('prevStagePoints', 0)
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('timeTillEnd', 0)
        self.showProgression = self._addCommand('showProgression')
        self.onProgressionAnimationCompleted = self._addCommand('onProgressionAnimationCompleted')
