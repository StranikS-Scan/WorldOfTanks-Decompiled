# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/base_quest_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.common.reward_model import RewardModel

class QuestStatusEnum(Enum):
    INPROGRESS = 'inProgress'
    REWARDNOTTAKEN = 'rewardNotTaken'
    COMPLETED = 'completed'
    WILLOPEN = 'willOpen'
    HIDDEN = 'hidden'


class QuestTypeEnum(Enum):
    SIMPLY = 'simply'
    EVENTABILITY = 'eventAbility'
    BOOSTER = 'booster'
    TANKMAN = 'tankman'
    HWXP = 'hwxp'


class BaseQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(BaseQuestModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getProgress(self):
        return self._getNumber(1)

    def setProgress(self, value):
        self._setNumber(1, value)

    def getAmount(self):
        return self._getNumber(2)

    def setAmount(self, value):
        self._setNumber(2, value)

    def getDeltaFrom(self):
        return self._getNumber(3)

    def setDeltaFrom(self, value):
        self._setNumber(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return RewardModel

    def getStatus(self):
        return QuestStatusEnum(self._getString(5))

    def setStatus(self, value):
        self._setString(5, value.value)

    def getAbilityName(self):
        return self._getString(6)

    def setAbilityName(self, value):
        self._setString(6, value)

    def getAbilityIcon(self):
        return self._getString(7)

    def setAbilityIcon(self, value):
        self._setString(7, value)

    def getIsDisabled(self):
        return self._getBool(8)

    def setIsDisabled(self, value):
        self._setBool(8, value)

    def getType(self):
        return QuestTypeEnum(self._getString(9))

    def setType(self, value):
        self._setString(9, value.value)

    def _initialize(self):
        super(BaseQuestModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('amount', 0)
        self._addNumberProperty('deltaFrom', 0)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('status')
        self._addStringProperty('abilityName', '')
        self._addStringProperty('abilityIcon', '')
        self._addBoolProperty('isDisabled', False)
        self._addStringProperty('type')
