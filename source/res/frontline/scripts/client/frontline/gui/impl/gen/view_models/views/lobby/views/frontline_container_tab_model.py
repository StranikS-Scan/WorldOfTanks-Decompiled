# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/frontline_container_tab_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TabType(Enum):
    PROGRESS = 'progress'
    REWARDS = 'rewards'
    INFO = 'info'


class FrontlineContainerTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(FrontlineContainerTabModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getType(self):
        return TabType(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getIsHighlighted(self):
        return self._getBool(2)

    def setIsHighlighted(self, value):
        self._setBool(2, value)

    def getResId(self):
        return self._getNumber(3)

    def setResId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(FrontlineContainerTabModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('type')
        self._addBoolProperty('isHighlighted', False)
        self._addNumberProperty('resId', 0)
