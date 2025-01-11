# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_quests_card_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CardState(Enum):
    SWITCH = 'switch'
    NOTAVAILABLE = 'notAvailable'
    AVAILABLE = 'available'
    PAUSE = 'pause'
    INPROGRESS = 'inProgress'
    DONES = 'doneSwitch'
    DONE = 'done'
    DONEP = 'donePause'
    DONEH = 'doneHonor'


class Pm3QuestsCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(Pm3QuestsCardModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getType(self):
        return CardState(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getSelectionAvailable(self):
        return self._getBool(2)

    def setSelectionAvailable(self, value):
        self._setBool(2, value)

    def getSelected(self):
        return self._getBool(3)

    def setSelected(self, value):
        self._setBool(3, value)

    def getIsLast(self):
        return self._getBool(4)

    def setIsLast(self, value):
        self._setBool(4, value)

    def getQuestName(self):
        return self._getString(5)

    def setQuestName(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(Pm3QuestsCardModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('type')
        self._addBoolProperty('selectionAvailable', False)
        self._addBoolProperty('selected', False)
        self._addBoolProperty('isLast', False)
        self._addStringProperty('questName', '')
