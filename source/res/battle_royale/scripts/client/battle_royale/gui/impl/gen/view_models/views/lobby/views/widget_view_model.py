# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/widget_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BattleStatus(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class Animation(Enum):
    NONE = 'none'
    BLINK = 'blink'


class WidgetViewModel(ViewModel):
    __slots__ = ('onWrapperInitialized',)

    def __init__(self, properties=4, commands=1):
        super(WidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getBattleStatus(self):
        return BattleStatus(self._getString(0))

    def setBattleStatus(self, value):
        self._setString(0, value.value)

    def getAnimation(self):
        return Animation(self._getString(1))

    def setAnimation(self, value):
        self._setString(1, value.value)

    def getCurrentProgression(self):
        return self._getNumber(2)

    def setCurrentProgression(self, value):
        self._setNumber(2, value)

    def getIsAlertMode(self):
        return self._getBool(3)

    def setIsAlertMode(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WidgetViewModel, self)._initialize()
        self._addStringProperty('battleStatus')
        self._addStringProperty('animation', Animation.NONE.value)
        self._addNumberProperty('currentProgression', 0)
        self._addBoolProperty('isAlertMode', False)
        self.onWrapperInitialized = self._addCommand('onWrapperInitialized')
