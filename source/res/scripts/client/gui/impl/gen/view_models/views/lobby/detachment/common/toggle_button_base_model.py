# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/toggle_button_base_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class ToggleButtonBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ToggleButtonBaseModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getIsActive(self):
        return self._getBool(2)

    def setIsActive(self, value):
        self._setBool(2, value)

    def getTooltipHeader(self):
        return self._getResource(3)

    def setTooltipHeader(self, value):
        self._setResource(3, value)

    def getTooltipBody(self):
        return self._getResource(4)

    def setTooltipBody(self, value):
        self._setResource(4, value)

    def _initialize(self):
        super(ToggleButtonBaseModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isActive', False)
        self._addResourceProperty('tooltipHeader', R.invalid())
        self._addResourceProperty('tooltipBody', R.invalid())
