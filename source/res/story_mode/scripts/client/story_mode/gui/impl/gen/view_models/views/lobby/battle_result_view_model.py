# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/battle_result_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from story_mode.gui.impl.gen.view_models.views.lobby.mission_progress_level_model import MissionProgressLevelModel
from story_mode.gui.impl.gen.view_models.views.lobby.progress_level_model import ProgressLevelModel
from story_mode.gui.impl.gen.view_models.views.lobby.reward_model import RewardModel

class BattleResultViewModel(ViewModel):
    __slots__ = ('onQuit', 'onContinue')

    def __init__(self, properties=13, commands=2):
        super(BattleResultViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def missionProgress(self):
        return self._getViewModel(0)

    @staticmethod
    def getMissionProgressType():
        return MissionProgressLevelModel

    def getMissionId(self):
        return self._getNumber(1)

    def setMissionId(self, value):
        self._setNumber(1, value)

    def getIsVictory(self):
        return self._getBool(2)

    def setIsVictory(self, value):
        self._setBool(2, value)

    def getTitle(self):
        return self._getResource(3)

    def setTitle(self, value):
        self._setResource(3, value)

    def getSubTitle(self):
        return self._getResource(4)

    def setSubTitle(self, value):
        self._setResource(4, value)

    def getInfoName(self):
        return self._getString(5)

    def setInfoName(self, value):
        self._setString(5, value)

    def getInfoDescription(self):
        return self._getString(6)

    def setInfoDescription(self, value):
        self._setString(6, value)

    def getVehicleName(self):
        return self._getString(7)

    def setVehicleName(self, value):
        self._setString(7, value)

    def getPlayerStatus(self):
        return self._getString(8)

    def setPlayerStatus(self, value):
        self._setString(8, value)

    def getIsDifficult(self):
        return self._getBool(9)

    def setIsDifficult(self, value):
        self._setBool(9, value)

    def getIsOnboarding(self):
        return self._getBool(10)

    def setIsOnboarding(self, value):
        self._setBool(10, value)

    def getProgressLevels(self):
        return self._getArray(11)

    def setProgressLevels(self, value):
        self._setArray(11, value)

    @staticmethod
    def getProgressLevelsType():
        return ProgressLevelModel

    def getRewards(self):
        return self._getArray(12)

    def setRewards(self, value):
        self._setArray(12, value)

    @staticmethod
    def getRewardsType():
        return RewardModel

    def _initialize(self):
        super(BattleResultViewModel, self)._initialize()
        self._addViewModelProperty('missionProgress', MissionProgressLevelModel())
        self._addNumberProperty('missionId', 0)
        self._addBoolProperty('isVictory', False)
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addStringProperty('infoName', '')
        self._addStringProperty('infoDescription', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('playerStatus', '')
        self._addBoolProperty('isDifficult', False)
        self._addBoolProperty('isOnboarding', False)
        self._addArrayProperty('progressLevels', Array())
        self._addArrayProperty('rewards', Array())
        self.onQuit = self._addCommand('onQuit')
        self.onContinue = self._addCommand('onContinue')
