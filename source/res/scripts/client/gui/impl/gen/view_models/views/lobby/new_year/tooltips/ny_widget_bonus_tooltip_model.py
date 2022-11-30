# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_widget_bonus_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TooltipState(Enum):
    NORMAL = 'normal'
    LEVELERROR = 'levelError'
    VEHICLEERROR = 'vehicleError'


class NyWidgetBonusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyWidgetBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTooltipState(self):
        return TooltipState(self._getString(0))

    def setTooltipState(self, value):
        self._setString(0, value.value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyWidgetBonusTooltipModel, self)._initialize()
        self._addStringProperty('tooltipState')
        self._addNumberProperty('level', 1)
