# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/views/progression_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from winback.gui.impl.gen.view_models.views.lobby.missions.battle_quests_model import BattleQuestsModel
from winback.gui.impl.gen.view_models.views.lobby.views.progress_level_model import ProgressLevelModel

class ProgressionState(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class ProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutClicked', 'onShowSelectableRewardView')
    ARG_STAGE_NUMBER = 'stage'
    WITHOUT_STAGE = -1

    def __init__(self, properties=8, commands=3):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleQuestsType():
        return BattleQuestsModel

    def getState(self):
        return ProgressionState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getCurProgressPoints(self):
        return self._getNumber(2)

    def setCurProgressPoints(self, value):
        self._setNumber(2, value)

    def getPrevProgressPoints(self):
        return self._getNumber(3)

    def setPrevProgressPoints(self, value):
        self._setNumber(3, value)

    def getPointsForLevel(self):
        return self._getNumber(4)

    def setPointsForLevel(self, value):
        self._setNumber(4, value)

    def getProgressLevels(self):
        return self._getArray(5)

    def setProgressLevels(self, value):
        self._setArray(5, value)

    @staticmethod
    def getProgressLevelsType():
        return ProgressLevelModel

    def getIsClaimRewardsAvailable(self):
        return self._getBool(6)

    def setIsClaimRewardsAvailable(self, value):
        self._setBool(6, value)

    def getProgressionName(self):
        return self._getString(7)

    def setProgressionName(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addViewModelProperty('battleQuests', BattleQuestsModel())
        self._addStringProperty('state')
        self._addNumberProperty('curProgressPoints', 0)
        self._addNumberProperty('prevProgressPoints', 0)
        self._addNumberProperty('pointsForLevel', 0)
        self._addArrayProperty('progressLevels', Array())
        self._addBoolProperty('isClaimRewardsAvailable', False)
        self._addStringProperty('progressionName', '')
        self.onClose = self._addCommand('onClose')
        self.onAboutClicked = self._addCommand('onAboutClicked')
        self.onShowSelectableRewardView = self._addCommand('onShowSelectableRewardView')
