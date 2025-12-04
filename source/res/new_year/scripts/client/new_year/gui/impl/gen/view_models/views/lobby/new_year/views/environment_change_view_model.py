# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/environment_change_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EnvironmentState(Enum):
    DAY = 'Day'
    AUTO = 'Auto'
    NIGHT = 'Night'


class EnvironmentChangeViewModel(ViewModel):
    __slots__ = ('onAnimationFinished', 'onAnimationFadeFinished')

    def __init__(self, properties=2, commands=2):
        super(EnvironmentChangeViewModel, self).__init__(properties=properties, commands=commands)

    def getSwitchTo(self):
        return EnvironmentState(self._getString(0))

    def setSwitchTo(self, value):
        self._setString(0, value.value)

    def getIsEnvironmentSwitched(self):
        return self._getBool(1)

    def setIsEnvironmentSwitched(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(EnvironmentChangeViewModel, self)._initialize()
        self._addStringProperty('switchTo')
        self._addBoolProperty('isEnvironmentSwitched', False)
        self.onAnimationFinished = self._addCommand('onAnimationFinished')
        self.onAnimationFadeFinished = self._addCommand('onAnimationFadeFinished')
