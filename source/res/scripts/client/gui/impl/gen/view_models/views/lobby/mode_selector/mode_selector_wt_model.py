# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_wt_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_wt_widget_model import ModeSelectorWtWidgetModel

class PerformanceRisk(Enum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class ModeSelectorWtModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(ModeSelectorWtModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(20)

    @staticmethod
    def getWidgetType():
        return ModeSelectorWtWidgetModel

    def getPerformanceRisk(self):
        return PerformanceRisk(self._getString(21))

    def setPerformanceRisk(self, value):
        self._setString(21, value.value)

    def _initialize(self):
        super(ModeSelectorWtModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorWtWidgetModel())
        self._addStringProperty('performanceRisk')
