# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/dialog_tankman_base_model.py
from frameworks.wulf import ViewModel

class DialogTankmanBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(DialogTankmanBaseModel, self).__init__(properties=properties, commands=commands)

    def getInvId(self):
        return self._getReal(0)

    def setInvId(self, value):
        self._setReal(0, value)

    def getIconName(self):
        return self._getString(1)

    def setIconName(self, value):
        self._setString(1, value)

    def getIsInSkin(self):
        return self._getBool(2)

    def setIsInSkin(self, value):
        self._setBool(2, value)

    def getIsFemale(self):
        return self._getBool(3)

    def setIsFemale(self, value):
        self._setBool(3, value)

    def getIsSelected(self):
        return self._getBool(4)

    def setIsSelected(self, value):
        self._setBool(4, value)

    def getRole(self):
        return self._getString(5)

    def setRole(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(DialogTankmanBaseModel, self)._initialize()
        self._addRealProperty('invId', 0.0)
        self._addStringProperty('iconName', '')
        self._addBoolProperty('isInSkin', False)
        self._addBoolProperty('isFemale', False)
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('role', '')
