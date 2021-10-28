# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/event_difficulty_item_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class StateEnum(Enum):
    DEFAULT = 'default'
    SELECTED = 'selected'
    DISABLED = 'disabled'
    LOCKED = 'locked'
    HIGHLIGHTED = 'highlighted'


class AnimationTypeEnum(Enum):
    NO_ANIMATION = 'noAmination'
    NEW = 'new'
    HINT = 'hint'


class EventDifficultyItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EventDifficultyItemModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getState(self):
        return StateEnum(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getAnimationType(self):
        return AnimationTypeEnum(self._getString(2))

    def setAnimationType(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(EventDifficultyItemModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addStringProperty('state')
        self._addStringProperty('animationType')
