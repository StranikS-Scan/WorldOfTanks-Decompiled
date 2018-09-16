# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/button_model.py
from frameworks.wulf.gui_constants import ResourceValue
from frameworks.wulf import ViewModel

class ButtonModel(ViewModel):
    __slots__ = ('onClicked',)

    def getRawLabel(self):
        return self._getString(0)

    def setRawLabel(self, value):
        self._setString(0, value)

    def getLabel(self):
        return self._getResource(1)

    def setLabel(self, value):
        self._setResource(1, value)

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def getIconAfterText(self):
        return self._getBool(4)

    def setIconAfterText(self, value):
        self._setBool(4, value)

    def _initialize(self):
        self._addStringProperty('rawLabel', '')
        self._addResourceProperty('label', ResourceValue.DEFAULT)
        self._addBoolProperty('isEnabled', True)
        self._addResourceProperty('icon', ResourceValue.DEFAULT)
        self._addBoolProperty('iconAfterText', True)
        self.onClicked = self._addCommand('onClicked')
