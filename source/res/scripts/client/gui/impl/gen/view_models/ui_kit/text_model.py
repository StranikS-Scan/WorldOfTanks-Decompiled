# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/text_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class TextModel(ViewModel):
    __slots__ = ()

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

    def _initialize(self):
        super(TextModel, self)._initialize()
        self._addStringProperty('rawLabel', '')
        self._addResourceProperty('label', Resource.INVALID)
        self._addBoolProperty('isEnabled', False)
