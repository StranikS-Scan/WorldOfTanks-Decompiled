# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/challenge_quest_progress_model.py
from gui.impl.gen.view_models.common.missions.challenge_mission_model import ChallengeMissionModel

class ChallengeQuestProgressModel(ChallengeMissionModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(ChallengeQuestProgressModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(12)

    def setId(self, value):
        self._setString(12, value)

    def getChallengeName(self):
        return self._getString(13)

    def setChallengeName(self, value):
        self._setString(13, value)

    def getNavigationEnabled(self):
        return self._getBool(14)

    def setNavigationEnabled(self, value):
        self._setBool(14, value)

    def getIsCompleted(self):
        return self._getBool(15)

    def setIsCompleted(self, value):
        self._setBool(15, value)

    def getCurrentProgress(self):
        return self._getNumber(16)

    def setCurrentProgress(self, value):
        self._setNumber(16, value)

    def getTotalProgress(self):
        return self._getNumber(17)

    def setTotalProgress(self, value):
        self._setNumber(17, value)

    def _initialize(self):
        super(ChallengeQuestProgressModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('challengeName', '')
        self._addBoolProperty('navigationEnabled', False)
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
