# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_fun_random_widget_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class SimpleFunProgressionStatus(Enum):
    DISABLED = 'disabled'
    ACTIVE = 'active'
    RESETTABLE = 'resettable'


class ModeSelectorFunRandomWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ModeSelectorFunRandomWidgetModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return SimpleFunProgressionStatus(self._getString(1))

    def setStatus(self, value):
        self._setString(1, value.value)

    def getCurrentStage(self):
        return self._getNumber(2)

    def setCurrentStage(self, value):
        self._setNumber(2, value)

    def getResetTimer(self):
        return self._getNumber(3)

    def setResetTimer(self, value):
        self._setNumber(3, value)

    def getStageCurrentPoints(self):
        return self._getNumber(4)

    def setStageCurrentPoints(self, value):
        self._setNumber(4, value)

    def getStageMaximumPoints(self):
        return self._getNumber(5)

    def setStageMaximumPoints(self, value):
        self._setNumber(5, value)

    def getConditionText(self):
        return self._getString(6)

    def setConditionText(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(ModeSelectorFunRandomWidgetModel, self)._initialize()
        self._addStringProperty('status')
        self._addNumberProperty('currentStage', -1)
        self._addNumberProperty('resetTimer', -1)
        self._addNumberProperty('stageCurrentPoints', -1)
        self._addNumberProperty('stageMaximumPoints', -1)
        self._addStringProperty('conditionText', '')
