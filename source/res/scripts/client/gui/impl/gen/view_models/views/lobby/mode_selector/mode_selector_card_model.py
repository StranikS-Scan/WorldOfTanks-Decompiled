# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_card_model.py
from frameworks.wulf import ViewModel

class ModeSelectorCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(ModeSelectorCardModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(0)

    def setIndex(self, value):
        self._setNumber(0, value)

    def getType(self):
        return self._getNumber(1)

    def setType(self, value):
        self._setNumber(1, value)

    def getResourcesFolderName(self):
        return self._getString(2)

    def setResourcesFolderName(self, value):
        self._setString(2, value)

    def getIsNew(self):
        return self._getBool(3)

    def setIsNew(self, value):
        self._setBool(3, value)

    def getIsSelected(self):
        return self._getBool(4)

    def setIsSelected(self, value):
        self._setBool(4, value)

    def getIsDisabled(self):
        return self._getBool(5)

    def setIsDisabled(self, value):
        self._setBool(5, value)

    def getIsInfoIconVisible(self):
        return self._getBool(6)

    def setIsInfoIconVisible(self, value):
        self._setBool(6, value)

    def getPriority(self):
        return self._getNumber(7)

    def setPriority(self, value):
        self._setNumber(7, value)

    def getColumn(self):
        return self._getNumber(8)

    def setColumn(self, value):
        self._setNumber(8, value)

    def getModeName(self):
        return self._getString(9)

    def setModeName(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(ModeSelectorCardModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addNumberProperty('type', 0)
        self._addStringProperty('resourcesFolderName', '')
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isInfoIconVisible', False)
        self._addNumberProperty('priority', 0)
        self._addNumberProperty('column', -1)
        self._addStringProperty('modeName', '')
