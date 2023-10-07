# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/retrain_tankman_model.py
from frameworks.wulf import ViewModel

class RetrainTankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RetrainTankmanModel, self).__init__(properties=properties, commands=commands)

    def getIconName(self):
        return self._getString(0)

    def setIconName(self, value):
        self._setString(0, value)

    def getIsInSkin(self):
        return self._getBool(1)

    def setIsInSkin(self, value):
        self._setBool(1, value)

    def getIsFemale(self):
        return self._getBool(2)

    def setIsFemale(self, value):
        self._setBool(2, value)

    def getRole(self):
        return self._getString(3)

    def setRole(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(RetrainTankmanModel, self)._initialize()
        self._addStringProperty('iconName', '')
        self._addBoolProperty('isInSkin', False)
        self._addBoolProperty('isFemale', False)
        self._addStringProperty('role', '')
