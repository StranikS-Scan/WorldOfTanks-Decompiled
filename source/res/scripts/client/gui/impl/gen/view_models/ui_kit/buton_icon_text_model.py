# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/buton_icon_text_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class ButonIconTextModel(ViewModel):
    __slots__ = ('onClicked', 'onSelected')

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getLabelString(self):
        return self._getString(1)

    def setLabelString(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def getIsSelected(self):
        return self._getBool(4)

    def setIsSelected(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(ButonIconTextModel, self)._initialize()
        self._addResourceProperty('label', Resource.INVALID)
        self._addStringProperty('labelString', '')
        self._addResourceProperty('icon', Resource.INVALID)
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isSelected', False)
        self.onClicked = self._addCommand('onClicked')
        self.onSelected = self._addCommand('onSelected')
