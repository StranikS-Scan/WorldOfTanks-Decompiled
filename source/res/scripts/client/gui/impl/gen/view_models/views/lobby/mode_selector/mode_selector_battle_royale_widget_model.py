# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_battle_royale_widget_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class BattleRoyaleProgressionStatus(Enum):
    DISABLED = 'disabled'
    ACTIVE = 'active'


class ModeSelectorBattleRoyaleWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ModeSelectorBattleRoyaleWidgetModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return BattleRoyaleProgressionStatus(self._getString(1))

    def setStatus(self, value):
        self._setString(1, value.value)

    def getCurrentStage(self):
        return self._getNumber(2)

    def setCurrentStage(self, value):
        self._setNumber(2, value)

    def getStageCurrentPoints(self):
        return self._getNumber(3)

    def setStageCurrentPoints(self, value):
        self._setNumber(3, value)

    def getStageMaximumPoints(self):
        return self._getNumber(4)

    def setStageMaximumPoints(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ModeSelectorBattleRoyaleWidgetModel, self)._initialize()
        self._addStringProperty('status')
        self._addNumberProperty('currentStage', -1)
        self._addNumberProperty('stageCurrentPoints', -1)
        self._addNumberProperty('stageMaximumPoints', -1)
