# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/race_equipment_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RaceEquipmentModel(ViewModel):
    __slots__ = ()

    def getIconSource(self):
        return self._getResource(0)

    def setIconSource(self, value):
        self._setResource(0, value)

    def getTooltipResId(self):
        return self._getNumber(1)

    def setTooltipResId(self, value):
        self._setNumber(1, value)

    def getTooltipType(self):
        return self._getString(2)

    def setTooltipType(self, value):
        self._setString(2, value)

    def getIntCD(self):
        return self._getNumber(3)

    def setIntCD(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(RaceEquipmentModel, self)._initialize()
        self._addResourceProperty('iconSource', R.invalid())
        self._addNumberProperty('tooltipResId', 0)
        self._addStringProperty('tooltipType', '')
        self._addNumberProperty('intCD', 0)
