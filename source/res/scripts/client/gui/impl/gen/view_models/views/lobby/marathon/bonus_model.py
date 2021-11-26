# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/marathon/bonus_model.py
from frameworks.wulf import ViewModel

class BonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BonusModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getLabel(self):
        return self._getString(2)

    def setLabel(self, value):
        self._setString(2, value)

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def getOverlayType(self):
        return self._getString(4)

    def setOverlayType(self, value):
        self._setString(4, value)

    def getDescription(self):
        return self._getString(5)

    def setDescription(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(BonusModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('label', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('overlayType', '')
        self._addStringProperty('description', '')
