# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/tooltips/challenges_banner_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.challenge_mission_model import ChallengeMissionModel

class ChallengesBannerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ChallengesBannerTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def mission(self):
        return self._getViewModel(0)

    @staticmethod
    def getMissionType():
        return ChallengeMissionModel

    def getTime(self):
        return self._getNumber(1)

    def setTime(self, value):
        self._setNumber(1, value)

    def getChallengeName(self):
        return self._getString(2)

    def setChallengeName(self, value):
        self._setString(2, value)

    def getCompletedMissions(self):
        return self._getNumber(3)

    def setCompletedMissions(self, value):
        self._setNumber(3, value)

    def getTotalMissions(self):
        return self._getNumber(4)

    def setTotalMissions(self, value):
        self._setNumber(4, value)

    def getRemainingAttempts(self):
        return self._getNumber(5)

    def setRemainingAttempts(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ChallengesBannerTooltipModel, self)._initialize()
        self._addViewModelProperty('mission', ChallengeMissionModel())
        self._addNumberProperty('time', 0)
        self._addStringProperty('challengeName', '')
        self._addNumberProperty('completedMissions', 0)
        self._addNumberProperty('totalMissions', 0)
        self._addNumberProperty('remainingAttempts', 0)
