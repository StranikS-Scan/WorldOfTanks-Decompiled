# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/widget_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BattleStatus(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class WidgetViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getBattleStatus(self):
        return BattleStatus(self._getString(0))

    def setBattleStatus(self, value):
        self._setString(0, value.value)

    def getCurrentProgression(self):
        return self._getNumber(1)

    def setCurrentProgression(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WidgetViewModel, self)._initialize()
        self._addStringProperty('battleStatus')
        self._addNumberProperty('currentProgression', 0)
