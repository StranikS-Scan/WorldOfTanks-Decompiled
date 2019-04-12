# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/button_common_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class ButtonCommonModel(ViewModel):
    __slots__ = ('onClicked', 'onSelected')

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getLabelString(self):
        return self._getString(1)

    def setLabelString(self, value):
        self._setString(1, value)

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def getIsSelected(self):
        return self._getBool(3)

    def setIsSelected(self, value):
        self._setBool(3, value)

    def getIsVisible(self):
        return self._getBool(4)

    def setIsVisible(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(ButtonCommonModel, self)._initialize()
        self._addResourceProperty('label', R.invalid())
        self._addStringProperty('labelString', '')
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isVisible', True)
        self.onClicked = self._addCommand('onClicked')
        self.onSelected = self._addCommand('onSelected')
