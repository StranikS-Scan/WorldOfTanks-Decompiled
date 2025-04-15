# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_hb_card_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class ModeSelectorHbCardModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(ModeSelectorHbCardModel, self).__init__(properties=properties, commands=commands)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(20))

    def setPerformanceRisk(self, value):
        self._setString(20, value.value)

    def _initialize(self):
        super(ModeSelectorHbCardModel, self)._initialize()
        self._addStringProperty('performanceRisk')
