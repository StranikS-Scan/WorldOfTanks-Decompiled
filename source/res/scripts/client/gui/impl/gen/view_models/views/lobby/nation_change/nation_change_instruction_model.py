# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/nation_change/nation_change_instruction_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NationChangeInstructionModel(ViewModel):
    __slots__ = ()

    def getImage(self):
        return self._getResource(0)

    def setImage(self, value):
        self._setResource(0, value)

    def getIsInstalled(self):
        return self._getBool(1)

    def setIsInstalled(self, value):
        self._setBool(1, value)

    def getIsActive(self):
        return self._getBool(2)

    def setIsActive(self, value):
        self._setBool(2, value)

    def getIntCD(self):
        return self._getNumber(3)

    def setIntCD(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(NationChangeInstructionModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addBoolProperty('isInstalled', False)
        self._addBoolProperty('isActive', False)
        self._addNumberProperty('intCD', 0)
