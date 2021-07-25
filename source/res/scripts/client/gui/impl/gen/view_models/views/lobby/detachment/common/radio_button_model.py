# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/radio_button_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RadioButtonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RadioButtonModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getLabel(self):
        return self._getResource(1)

    def setLabel(self, value):
        self._setResource(1, value)

    def getIsDisable(self):
        return self._getBool(2)

    def setIsDisable(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(RadioButtonModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addResourceProperty('label', R.invalid())
        self._addBoolProperty('isDisable', False)
