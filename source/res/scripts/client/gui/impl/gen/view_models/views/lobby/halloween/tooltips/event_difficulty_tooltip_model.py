# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/tooltips/event_difficulty_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class StateEnum(Enum):
    DEFAULT = 'default'
    SELECTED = 'selected'
    LOCKED = 'locked'


class EventDifficultyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(EventDifficultyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getCurrent(self):
        return self._getNumber(1)

    def setCurrent(self, value):
        self._setNumber(1, value)

    def getTotal(self):
        return self._getNumber(2)

    def setTotal(self, value):
        self._setNumber(2, value)

    def getState(self):
        return StateEnum(self._getString(3))

    def setState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(EventDifficultyTooltipModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
        self._addStringProperty('state')
