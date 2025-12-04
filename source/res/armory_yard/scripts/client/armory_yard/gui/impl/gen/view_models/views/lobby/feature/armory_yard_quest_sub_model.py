# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_quest_sub_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_quest_model import ArmoryYardQuestModel

class QuestStatus(Enum):
    DONE = 'done'
    UNDONESUBSCRIPTION = 'undoneSubscription'
    LOCKED = 'notAvailable'
    DISABLED = 'disabled'
    ACTIVE = ''


class ArmoryYardQuestSubModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ArmoryYardQuestSubModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsType():
        return ArmoryYardQuestModel

    def getStatus(self):
        return QuestStatus(self._getString(1))

    def setStatus(self, value):
        self._setString(1, value.value)

    def getTokenQuestID(self):
        return self._getString(2)

    def setTokenQuestID(self, value):
        self._setString(2, value)

    def getConditionID(self):
        return self._getNumber(3)

    def setConditionID(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ArmoryYardQuestSubModel, self)._initialize()
        self._addArrayProperty('quests', Array())
        self._addStringProperty('status')
        self._addStringProperty('tokenQuestID', '')
        self._addNumberProperty('conditionID', 0)
