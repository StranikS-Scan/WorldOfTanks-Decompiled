# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/challenge_missions/challenge_quest_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.challenge_mission_model import ChallengeMissionModel

class ChallengeState(Enum):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    FAILED = 'failed'
    COMPLETED = 'completed'


class ChallengeQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(ChallengeQuestModel, self).__init__(properties=properties, commands=commands)

    def getChallengeID(self):
        return self._getNumber(0)

    def setChallengeID(self, value):
        self._setNumber(0, value)

    def getState(self):
        return ChallengeState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def getPriority(self):
        return self._getNumber(3)

    def setPriority(self, value):
        self._setNumber(3, value)

    def getExpireTime(self):
        return self._getNumber(4)

    def setExpireTime(self, value):
        self._setNumber(4, value)

    def getAttempts(self):
        return self._getNumber(5)

    def setAttempts(self, value):
        self._setNumber(5, value)

    def getRemainingAttempts(self):
        return self._getNumber(6)

    def setRemainingAttempts(self, value):
        self._setNumber(6, value)

    def getCompletedMissions(self):
        return self._getNumber(7)

    def setCompletedMissions(self, value):
        self._setNumber(7, value)

    def getTotalMissions(self):
        return self._getNumber(8)

    def setTotalMissions(self, value):
        self._setNumber(8, value)

    def getChallengeName(self):
        return self._getString(9)

    def setChallengeName(self, value):
        self._setString(9, value)

    def getIsNew(self):
        return self._getBool(10)

    def setIsNew(self, value):
        self._setBool(10, value)

    def getRemainingFreeRestarts(self):
        return self._getNumber(11)

    def setRemainingFreeRestarts(self, value):
        self._setNumber(11, value)

    def getRestartCost(self):
        return self._getNumber(12)

    def setRestartCost(self, value):
        self._setNumber(12, value)

    def getCurrencyType(self):
        return self._getString(13)

    def setCurrencyType(self, value):
        self._setString(13, value)

    def getIsEnoughMoney(self):
        return self._getBool(14)

    def setIsEnoughMoney(self, value):
        self._setBool(14, value)

    def getMissions(self):
        return self._getArray(15)

    def setMissions(self, value):
        self._setArray(15, value)

    @staticmethod
    def getMissionsType():
        return ChallengeMissionModel

    def getMainRewardType(self):
        return self._getString(16)

    def setMainRewardType(self, value):
        self._setString(16, value)

    def getCompletions(self):
        return self._getNumber(17)

    def setCompletions(self, value):
        self._setNumber(17, value)

    def getAllowedCompletions(self):
        return self._getNumber(18)

    def setAllowedCompletions(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(ChallengeQuestModel, self)._initialize()
        self._addNumberProperty('challengeID', 0)
        self._addStringProperty('state')
        self._addStringProperty('type', '')
        self._addNumberProperty('priority', 0)
        self._addNumberProperty('expireTime', 0)
        self._addNumberProperty('attempts', 0)
        self._addNumberProperty('remainingAttempts', 0)
        self._addNumberProperty('completedMissions', 0)
        self._addNumberProperty('totalMissions', 0)
        self._addStringProperty('challengeName', '')
        self._addBoolProperty('isNew', False)
        self._addNumberProperty('remainingFreeRestarts', 0)
        self._addNumberProperty('restartCost', 0)
        self._addStringProperty('currencyType', '')
        self._addBoolProperty('isEnoughMoney', False)
        self._addArrayProperty('missions', Array())
        self._addStringProperty('mainRewardType', '')
        self._addNumberProperty('completions', 0)
        self._addNumberProperty('allowedCompletions', 0)
