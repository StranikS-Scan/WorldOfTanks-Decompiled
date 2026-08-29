# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/impl/gen/view_models/views/battle/battle_page/fall_tanks_battle_widget_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class WidgetState(Enum):
    DISABLED = 'disabled'
    INRACE = 'inRace'
    FINISHED = 'finished'
    NOTFINISHED = 'notFinished'


class FallTanksBattleWidgetModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(FallTanksBattleWidgetModel, self).__init__(properties=properties, commands=commands)

    def getObservable(self):
        return self._getBool(0)

    def setObservable(self, value):
        self._setBool(0, value)

    def getCheckpoint(self):
        return self._getNumber(1)

    def setCheckpoint(self, value):
        self._setNumber(1, value)

    def getPosition(self):
        return self._getNumber(2)

    def setPosition(self, value):
        self._setNumber(2, value)

    def getSpentTime(self):
        return self._getReal(3)

    def setSpentTime(self, value):
        self._setReal(3, value)

    def getState(self):
        return WidgetState(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(FallTanksBattleWidgetModel, self)._initialize()
        self._addBoolProperty('observable', False)
        self._addNumberProperty('checkpoint', -1)
        self._addNumberProperty('position', 0)
        self._addRealProperty('spentTime', 0.0)
        self._addStringProperty('state', WidgetState.DISABLED.value)
