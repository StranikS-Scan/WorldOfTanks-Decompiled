# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_resource_converter_info_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ConverterInfoTooltipType(Enum):
    FROM = 'from'
    TO = 'to'


class NyResourceConverterInfoTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyResourceConverterInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTooltipType(self):
        return ConverterInfoTooltipType(self._getString(0))

    def setTooltipType(self, value):
        self._setString(0, value.value)

    def getMultiple(self):
        return self._getNumber(1)

    def setMultiple(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyResourceConverterInfoTooltipModel, self)._initialize()
        self._addStringProperty('tooltipType')
        self._addNumberProperty('multiple', 0)
