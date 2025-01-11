# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_card_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SmallCardState(Enum):
    SWITCH = 'switch'
    NOTAVAILABLE = 'notAvailable'
    AVAILABLE = 'available'
    PAUSE = 'pause'
    INPROGRESS = 'inProgress'
    DONES = 'doneSwitch'
    DONE = 'done'
    DONEP = 'donePause'
    DONEH = 'doneHonor'


class Pm3CardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(Pm3CardModel, self).__init__(properties=properties, commands=commands)

    def getQuestId(self):
        return self._getNumber(0)

    def setQuestId(self, value):
        self._setNumber(0, value)

    def getState(self):
        return SmallCardState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getIsLast(self):
        return self._getBool(3)

    def setIsLast(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(Pm3CardModel, self)._initialize()
        self._addNumberProperty('questId', 0)
        self._addStringProperty('state')
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isLast', False)
