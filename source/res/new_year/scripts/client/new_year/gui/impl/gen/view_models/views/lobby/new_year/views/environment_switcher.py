# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/environment_switcher.py
from enum import Enum
from frameworks.wulf import ViewModel

class EnvironmentState(Enum):
    DAY = 'Day'
    AUTO = 'Auto'
    NIGHT = 'Night'


class EnvironmentSwitcher(ViewModel):
    __slots__ = ('onSwitch',)

    def __init__(self, properties=3, commands=1):
        super(EnvironmentSwitcher, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return EnvironmentState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getMode(self):
        return EnvironmentState(self._getString(1))

    def setMode(self, value):
        self._setString(1, value.value)

    def getArrowDegree(self):
        return self._getNumber(2)

    def setArrowDegree(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(EnvironmentSwitcher, self)._initialize()
        self._addStringProperty('state')
        self._addStringProperty('mode')
        self._addNumberProperty('arrowDegree', 0)
        self.onSwitch = self._addCommand('onSwitch')
