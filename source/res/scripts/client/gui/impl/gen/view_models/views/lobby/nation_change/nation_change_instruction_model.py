# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/nation_change/nation_change_instruction_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NationChangeInstructionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NationChangeInstructionModel, self).__init__(properties=properties, commands=commands)

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

    def getIsPerkReplace(self):
        return self._getBool(3)

    def setIsPerkReplace(self, value):
        self._setBool(3, value)

    def getIntCD(self):
        return self._getNumber(4)

    def setIntCD(self, value):
        self._setNumber(4, value)

    def getLayoutIDx(self):
        return self._getNumber(5)

    def setLayoutIDx(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(NationChangeInstructionModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addBoolProperty('isInstalled', False)
        self._addBoolProperty('isActive', False)
        self._addBoolProperty('isPerkReplace', False)
        self._addNumberProperty('intCD', 0)
        self._addNumberProperty('layoutIDx', 0)
