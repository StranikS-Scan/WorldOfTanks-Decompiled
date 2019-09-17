# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/race_equipment_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RaceEquipmentTooltipModel(ViewModel):
    __slots__ = ()

    def getIconSource(self):
        return self._getResource(0)

    def setIconSource(self, value):
        self._setResource(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(RaceEquipmentTooltipModel, self)._initialize()
        self._addResourceProperty('iconSource', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('description', R.invalid())
