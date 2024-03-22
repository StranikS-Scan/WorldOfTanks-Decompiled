# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/clan_supply/pages/quest_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class QuestStatus(IntEnum):
    DISABLED = 0
    IN_PROGRESS = 1
    REWARD_AVAILABLE = 2
    REWARD_PENDING = 3
    COMPLETE = 4


class QuestCondition(Enum):
    FRAGS = 'frags'
    FULL_DAMAGE = 'fullDamage'
    EXP = 'exp'
    WIN = 'win'


class QuestSquadState(Enum):
    SOLO = 'solo'
    PLATOON = 'platoon'
    SOLO_AND_PLATOON = 'soloAndPlatoon'
    DETACHMENT = 'detachment'


class QuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(QuestModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getRequiredProgress(self):
        return self._getNumber(2)

    def setRequiredProgress(self, value):
        self._setNumber(2, value)

    def getMainCondition(self):
        return QuestCondition(self._getString(3))

    def setMainCondition(self, value):
        self._setString(3, value.value)

    def getMainSquadState(self):
        return QuestSquadState(self._getString(4))

    def setMainSquadState(self, value):
        self._setString(4, value.value)

    def getAlternativeCondition(self):
        return QuestCondition(self._getString(5))

    def setAlternativeCondition(self, value):
        self._setString(5, value.value)

    def getAlternativeSquadState(self):
        return QuestSquadState(self._getString(6))

    def setAlternativeSquadState(self, value):
        self._setString(6, value.value)

    def getConditionParams(self):
        return self._getString(7)

    def setConditionParams(self, value):
        self._setString(7, value)

    def getStatus(self):
        return QuestStatus(self._getNumber(8))

    def setStatus(self, value):
        self._setNumber(8, value.value)

    def getRewards(self):
        return self._getArray(9)

    def setRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(QuestModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('requiredProgress', 0)
        self._addStringProperty('mainCondition')
        self._addStringProperty('mainSquadState')
        self._addStringProperty('alternativeCondition')
        self._addStringProperty('alternativeSquadState')
        self._addStringProperty('conditionParams', '')
        self._addNumberProperty('status')
        self._addArrayProperty('rewards', Array())
